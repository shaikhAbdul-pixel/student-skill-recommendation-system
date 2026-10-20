"""Generate reproducible fictional examples. No scraped or real student records."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.catalog import ROOT, EDUCATION, STREAMS, TRACKS, INTERESTS, SKILLS
from src.profiles import features


def generate(seed=42, per_track=60):
    rng = random.Random(seed)
    records, seen = [], set()
    for track, spec in TRACKS.items():
        for number in range(per_track):
            while True:
                education = EDUCATION[number % len(EDUCATION)]
                interests = rng.sample(spec["interests"], rng.randint(1, 3))
                # Mixed signals keep this a demo of ranking rather than an exact goal lookup.
                if rng.random() < 0.40:
                    interests.append(rng.choice(INTERESTS))
                skills = rng.sample(spec["skills"], rng.randint(0, min(3, len(spec["skills"]))))
                if rng.random() < 0.25:
                    skills.append(rng.choice(SKILLS))
                goal_pool = spec["goals"] if rng.random() > 0.18 else rng.choice(list(TRACKS.values()))["goals"]
                row = {"id": f"DEMO-{len(records)+1:04d}", "source": "synthetic_demo_v1",
                       "education": education, "stream": rng.choice(STREAMS),
                       "skills": sorted(set(skills)), "interests": sorted(set(interests)),
                       "goal": rng.choice(goal_pool) if rng.random() > 0.20 else "", "track": track}
                key = json.dumps(features(row), sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    records.append(row)
                    break
    return records


if __name__ == "__main__":
    path = ROOT / "data" / "demo_profiles.json"
    path.parent.mkdir(exist_ok=True)
    records = generate()
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} SYNTHETIC examples to {path}")
