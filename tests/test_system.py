"""Behaviour and integration checks. Run: python -m unittest discover -v"""
import json
import os
from pathlib import Path
import tempfile
import unittest
import numpy as np
from streamlit.testing.v1 import AppTest
from src.catalog import ROOT, EDUCATION, TRACKS, PREREQUISITES, SKILLS, INTERESTS, load_courses
from src.engine import Recommender, load_profiles
from src.evaluation import evaluate
from src.storage import save_plan, list_plans, delete_plans
from scripts.generate_demo_data import generate


def profile(**changes):
    result = {"education": "Class 12", "stream": "Science", "skills": ["Computer basics"],
              "interests": ["Coding", "Websites"], "goal": "Build websites and apps"}
    return {**result, **changes}


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_profiles()
        cls.engine = Recommender(cls.records)

    def test_all_education_levels_accept_beginners(self):
        for education in EDUCATION:
            with self.subTest(education=education):
                result = self.engine.recommend(profile(education=education, skills=[]))
                self.assertEqual(result["paths"][0]["track"], "Software Development")
                self.assertTrue(result["paths"][0]["ready_skills"])

    def test_recommendation_changes_with_interests_and_goals(self):
        cases = [("Design", "Create visual designs", "Design & Creativity"),
                 ("Data", "Become a data analyst", "Data Analytics"),
                 ("Finance", "Manage a business", "Business & Finance")]
        for interest, goal, expected in cases:
            with self.subTest(track=expected):
                result = self.engine.recommend(profile(skills=[], interests=[interest], goal=goal))
                self.assertEqual(expected, result["paths"][0]["track"])

    def test_known_skills_and_prerequisites(self):
        known = ["Python", "Statistics basics"]
        result = self.engine.recommend(profile(skills=known, interests=["Data"], goal="Become a data analyst"))
        path = result["paths"][0]
        self.assertNotIn("Python", path["ready_skills"])
        self.assertIn("Pandas", path["ready_skills"])
        beginner = self.engine.recommend(profile(skills=[], interests=["Data"], goal="Become a data analyst"))
        self.assertIn("Pandas", beginner["paths"][0]["later_skills"])
        self.assertFalse(any(c["id"] == "pandas" for c in beginner["paths"][0]["courses"]))

    def test_all_current_skills_are_never_recommended_again(self):
        result = self.engine.recommend(profile(skills=SKILLS))
        for path in result["paths"]:
            self.assertEqual(path["ready_skills"], [])
            self.assertEqual(path["courses"], [])

    def test_invalid_empty_and_unsupported_profiles(self):
        for changes in [{"education": "Unknown"}, {"skills": ["Invented skill"]},
                        {"skills": [], "interests": [], "goal": "  "},
                        {"skills": [], "interests": [], "goal": "xxyyzz asteroid astronaut"}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.engine.recommend(profile(**changes))

    def test_every_path_has_a_resource_and_correct_skill_gaps(self):
        for track, spec in TRACKS.items():
            with self.subTest(track=track):
                result = self.engine.recommend(profile(skills=[], interests=spec["interests"], goal=spec["goals"][0]))
                top = result["paths"][0]
                self.assertEqual(top["track"], track)
                self.assertTrue(top["courses"])
                self.assertFalse(set(top["ready_skills"]) & set(top["later_skills"]))
                self.assertEqual(set(spec["skills"]), set(top["ready_skills"] + top["later_skills"]))
                for skill in top["ready_skills"]:
                    self.assertFalse(PREREQUISITES.get(skill))

    def test_scores_are_finite_and_reproducible(self):
        first = self.engine.score([profile()])
        second = self.engine.score([profile()])
        for name in first:
            np.testing.assert_array_equal(first[name], second[name])
            self.assertTrue(np.isfinite(first[name]).all())
            self.assertAlmostEqual(float(first[name].sum()), 1)

    def test_generator_and_data_integrity(self):
        self.assertEqual(generate(), self.records)
        self.assertEqual(len(self.records), 420)
        self.assertEqual({r["source"] for r in self.records}, {"synthetic_demo_v1"})
        for track in TRACKS:
            self.assertEqual({r["education"] for r in self.records if r["track"] == track}, set(EDUCATION))
        for c in load_courses():
            self.assertTrue(c["url"].startswith("https://"))
            self.assertTrue(set(c["skills"]).issubset(SKILLS))

    def test_holdout_has_no_duplicate_overlap_and_matches_saved_report(self):
        report = evaluate(self.records)
        self.assertEqual(report["feature_overlap_count"], 0)
        self.assertEqual(report["train_rows"] + report["test_rows"], report["unique_rows"])
        self.assertEqual(sum(map(sum, report["hybrid_confusion_matrix"])), report["test_rows"])
        saved = json.loads((ROOT / "reports" / "evaluation.json").read_text())
        self.assertEqual(saved["dataset_sha256"], report["dataset_sha256"])
        self.assertEqual(saved["metrics"], report["metrics"])


class StorageTests(unittest.TestCase):
    def test_save_isolation_and_delete(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "plans.db"
            payload = {"goal": "Student's project; SELECT * FROM plans", "paths": []}
            save_plan("session-a", payload, database)
            save_plan("session-b", {"goal": "Another plan"}, database)
            self.assertEqual(list_plans("session-a", database)[0]["payload"], payload)
            self.assertEqual(len(list_plans("session-b", database)), 1)
            delete_plans("session-a", database)
            self.assertEqual(list_plans("session-a", database), [])
            self.assertEqual(len(list_plans("session-b", database)), 1)


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.original_db = os.environ.get("SKILLREC_DB")
        os.environ["SKILLREC_DB"] = str(Path(self.folder.name) / "test.db")
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()

    def tearDown(self):
        if self.original_db is None:
            os.environ.pop("SKILLREC_DB", None)
        else:
            os.environ["SKILLREC_DB"] = self.original_db
        self.folder.cleanup()

    def click_label(self, label):
        next(b for b in self.app.button if b.label == label).click().run()

    def test_empty_validation_then_sample_results_save_and_delete(self):
        self.assertFalse(self.app.exception)
        self.click_label("Find my skill path →")
        self.assertTrue(self.app.error)
        self.click_label("Try a sample profile")
        self.click_label("Find my skill path →")
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state.result["paths"][0]["track"], "Software Development")
        self.click_label("Save this plan locally")
        self.app.radio[0].set_value("Saved plans").run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any(s.label == "Choose a saved plan" for s in self.app.selectbox))
        self.click_label("Delete this session's saved plans")
        self.assertFalse(self.app.exception)
        self.assertTrue(any("No saved plans" in i.value for i in self.app.info))

    def test_pages_and_all_education_levels(self):
        self.click_label("Try a sample profile")
        for level in EDUCATION:
            self.app.selectbox(key="education").set_value(level)
            self.click_label("Find my skill path →")
            self.assertFalse(self.app.exception)
            self.assertEqual(self.app.session_state.result["profile"]["education"], level)
        for page in ["Model lab", "Project guide", "Saved plans", "Discover your path"]:
            self.app.radio[0].set_value(page).run()
            self.assertFalse(self.app.exception)


if __name__ == "__main__":
    unittest.main()
