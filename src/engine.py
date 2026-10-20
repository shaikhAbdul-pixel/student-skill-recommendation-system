"""Decision Tree + KNN + cosine prototype ranking, followed by skill-gap rules."""
import json
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from src.catalog import ROOT, TRACKS, PREREQUISITES, load_courses
from src.profiles import features, validate_profile


def load_profiles(path=None):
    return json.loads((path or ROOT / "data" / "demo_profiles.json").read_text(encoding="utf-8"))


class Recommender:
    """Small enough to train on app startup; no opaque downloaded model files."""

    def __init__(self, records):
        self.vectorizer = DictVectorizer(sparse=True)
        self.matrix = normalize(self.vectorizer.fit_transform([features(r) for r in records]))
        self.labels = np.array([r["track"] for r in records])
        self.classes = np.array(sorted(set(self.labels)))
        self.tree = DecisionTreeClassifier(max_depth=6, min_samples_leaf=3, random_state=42)
        self.knn = KNeighborsClassifier(n_neighbors=min(7, len(records)), metric="cosine",
                                        algorithm="brute", weights="distance")
        self.tree.fit(self.matrix, self.labels)
        self.knn.fit(self.matrix, self.labels)
        # A mean feature vector per track is a simple, explainable content prototype.
        self.centroids = np.vstack([
            np.asarray(self.matrix[self.labels == label].mean(axis=0)).ravel()
            for label in self.classes
        ])

    def score(self, profiles):
        matrix = normalize(self.vectorizer.transform([features(p) for p in profiles]))
        tree = self.tree.predict_proba(matrix)
        knn = self.knn.predict_proba(matrix)
        # sklearn classifiers and our prototypes use the same sorted class order.
        assert list(self.tree.classes_) == list(self.knn.classes_) == list(self.classes)
        cosine_raw = cosine_similarity(matrix, self.centroids)
        totals = cosine_raw.sum(axis=1, keepdims=True)
        cosine = np.divide(cosine_raw, totals, out=np.zeros_like(cosine_raw), where=totals != 0)
        return {"Decision Tree": tree, "KNN": knn, "Cosine Similarity": cosine,
                "Hybrid": 0.35 * tree + 0.35 * knn + 0.30 * cosine}

    def recommend(self, profile):
        validate_profile(profile)
        known_features = [key for key in features(profile)
                          if not key.startswith(("education:", "stream:"))
                          and key in self.vectorizer.vocabulary_]
        if not known_features:
            raise ValueError("This goal is outside the demo vocabulary. Select a listed interest or skill, or use a suggested career goal.")
        scores = self.score([profile])
        order = np.argsort(-scores["Hybrid"][0], kind="stable")[:3]
        paths = []
        courses = load_courses()
        for index in order:
            track = str(self.classes[index])
            spec = TRACKS[track]
            existing = set(profile.get("skills", []))
            missing = [s for s in spec["skills"] if s not in existing]
            # Only ready skills are suggested now; prerequisites remain visible as next steps.
            ready = [s for s in missing if set(PREREQUISITES.get(s, [])).issubset(existing)]
            later = [s for s in missing if s not in ready]
            matched = sorted(set(profile.get("interests", [])) & set(spec["interests"]))
            matched_skills = sorted(existing & set(spec["skills"]))
            recommendations = []
            for course in courses:
                teaches = [s for s in course["skills"] if s in ready]
                if teaches and set(course["prerequisites"]).issubset(existing):
                    recommendations.append({**course, "addresses": teaches})
            # One resource can teach multiple missing skills; show most coverage first.
            recommendations.sort(key=lambda c: (-len(c["addresses"]), c["title"]))
            paths.append({
                "track": track, "score": round(float(scores["Hybrid"][0, index]), 4),
                "components": {name: round(float(value[0, index]), 4) for name, value in scores.items() if name != "Hybrid"},
                "matched_interests": matched, "matched_skills": matched_skills,
                "ready_skills": ready, "later_skills": later,
                "later_prerequisites": {s: PREREQUISITES[s] for s in later},
                "courses": recommendations[:3], "project": spec["project"],
            })
        notes = ["Demo ranking from synthetic profiles. Ranking scores are not model accuracy, aptitude scores or job probabilities."]
        if paths[0]["score"] - paths[1]["score"] < 0.12:
            notes.append("Your signals span multiple paths. Compare the alternatives before choosing.")
        if profile["education"] in ["Class 10", "Class 12"]:
            notes.append("Start with a short foundation activity; these paths do not determine your school stream or admission eligibility.")
        return {"profile": profile, "paths": paths, "notes": notes, "data_source": "synthetic_demo_v1"}
