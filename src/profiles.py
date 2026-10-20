"""Validate profiles and convert them into transparent numerical features."""
import re
from src.catalog import EDUCATION, STREAMS, SKILLS, INTERESTS

STOP_WORDS = {"a", "an", "the", "to", "and", "in", "of", "i", "want", "be", "become", "my", "with", "as"}


def validate_profile(profile):
    if profile.get("education") not in EDUCATION:
        raise ValueError("Choose a supported education level.")
    if profile.get("stream") not in STREAMS:
        raise ValueError("Choose a supported stream.")
    for key, allowed in [("skills", SKILLS), ("interests", INTERESTS)]:
        values = profile.get(key, [])
        if not isinstance(values, list) or any(v not in allowed for v in values):
            raise ValueError(f"Use the listed {key} options.")
    if not isinstance(profile.get("goal", ""), str):
        raise ValueError("Career goal must be text.")
    if len(profile.get("goal", "")) > 500:
        raise ValueError("Keep your career goal within 500 characters.")
    if not (profile.get("skills") or profile.get("interests") or profile.get("goal", "").strip()):
        raise ValueError("Add at least one skill, interest or career goal to personalise your plan.")


def features(profile):
    """One-hot categories plus weighted multi-hot skills/interests and goal words.

    Education/stream carry less weight to avoid making stream a career restriction.
    We never use row ID, demo label, or data provenance as input features.
    """
    result = {f"education:{profile['education']}": 0.3,
              f"stream:{profile['stream']}": 0.3}
    for skill in set(profile.get("skills", [])):
        result[f"skill:{skill}"] = 0.7
    for interest in set(profile.get("interests", [])):
        result[f"interest:{interest}"] = 1.0
    for word in set(re.findall(r"[a-z]+", profile.get("goal", "").lower())) - STOP_WORDS:
        result[f"goal:{word}"] = 0.65
    return result
