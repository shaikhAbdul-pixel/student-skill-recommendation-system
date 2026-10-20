"""Editable, human-curated skill paths. These are examples, not labour-market data."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
EDUCATION = ["Class 10", "Class 12", "Diploma", "Undergraduate", "Graduate"]
STREAMS = ["General / Not decided", "Science", "Commerce", "Arts / Humanities",
           "Computer Science / IT", "Engineering", "Management", "Other"]

# Ordered from foundations to next steps; prerequisites are enforced by the engine.
TRACKS = {
    "Software Development": {
        "interests": ["Coding", "Websites", "Problem solving", "Technology"],
        "goals": ["Build websites and apps", "Become a software developer", "Create useful software"],
        "skills": ["Computer basics", "Programming logic", "HTML & CSS", "Python", "Git", "JavaScript"],
        "project": "Build a personal portfolio website with a working contact-form mockup.",
    },
    "Data Analytics": {
        "interests": ["Data", "Mathematics", "Research", "Problem solving"],
        "goals": ["Analyse data and create reports", "Become a data analyst", "Find patterns in datasets"],
        "skills": ["Spreadsheets", "Statistics basics", "Python", "SQL", "Data visualisation", "Pandas"],
        "project": "Analyse a public or synthetic dataset and explain three findings with charts.",
    },
    "Design & Creativity": {
        "interests": ["Art", "Design", "Websites", "Storytelling"],
        "goals": ["Design user friendly products", "Become a UI UX designer", "Create visual designs"],
        "skills": ["Visual design", "User research", "Figma", "Prototyping", "Accessibility"],
        "project": "Design and test a three-screen student app prototype with two volunteers.",
    },
    "Digital Marketing": {
        "interests": ["Social media", "Writing", "Business", "Storytelling"],
        "goals": ["Grow a brand online", "Become a digital marketer", "Create social media campaigns"],
        "skills": ["Content writing", "Marketing basics", "SEO", "Social media strategy", "Marketing analytics"],
        "project": "Create a sample campaign with audience, three posts and measurable objectives.",
    },
    "Business & Finance": {
        "interests": ["Business", "Finance", "Mathematics", "Leadership"],
        "goals": ["Manage a business", "Work in business finance", "Start a small enterprise"],
        "skills": ["Spreadsheets", "Business communication", "Accounting basics", "Budgeting", "Business analysis"],
        "project": "Create a fictional small-business budget and explain its costs and assumptions.",
    },
    "Engineering & Technology": {
        "interests": ["Electronics", "Machines", "Technology", "Mathematics"],
        "goals": ["Build electronic projects", "Explore engineering design", "Understand machines and circuits"],
        "skills": ["Mathematics foundations", "Engineering drawing", "Circuit basics", "Python", "CAD basics"],
        "project": "Model a simple circuit in a simulator and explain each component's role.",
    },
    "Communication & Teaching": {
        "interests": ["Teaching", "Writing", "Leadership", "Research"],
        "goals": ["Teach and explain concepts", "Improve professional communication", "Create learning materials"],
        "skills": ["Communication", "Presentation skills", "Research literacy", "Lesson planning", "Digital teaching tools"],
        "project": "Prepare a five-minute lesson, a slide deck and a short feedback questionnaire.",
    },
}
PREREQUISITES = {
    "JavaScript": ["HTML & CSS"], "Git": ["Computer basics"],
    "Pandas": ["Python"], "Data visualisation": ["Statistics basics"],
    "Prototyping": ["Figma"], "Marketing analytics": ["Marketing basics"],
    "Business analysis": ["Spreadsheets"], "CAD basics": ["Engineering drawing"],
    "Digital teaching tools": ["Lesson planning"],
}
INTERESTS = sorted({i for t in TRACKS.values() for i in t["interests"]})
SKILLS = sorted({s for t in TRACKS.values() for s in t["skills"]})
GOALS = [g for t in TRACKS.values() for g in t["goals"]]


def load_courses():
    """Courses/resources are local catalogue entries; the app makes no live API calls."""
    return json.loads((ROOT / "data" / "courses.json").read_text(encoding="utf-8"))
