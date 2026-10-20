"""Run with: python -m streamlit run app.py"""
import json
import os
import sqlite3
import uuid
from pathlib import Path
import pandas as pd
import streamlit as st
from src.catalog import ROOT, EDUCATION, STREAMS, SKILLS, INTERESTS, GOALS, TRACKS, load_courses
from src.engine import Recommender, load_profiles
from src.evaluation import evaluate
from src.storage import save_plan, list_plans, delete_plans

st.set_page_config(page_title="Student Skill Recommendation System", page_icon="🎓", layout="wide")
st.markdown("<style>" + (ROOT / "assets" / "style.css").read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)


@st.cache_resource
def get_engine(dataset_revision):
    # The timestamp key invalidates the cache after editing the demo data.
    return Recommender(load_profiles())


@st.cache_data
def get_evaluation(dataset_revision):
    return evaluate(load_profiles())


def db_path():
    # Tests can redirect storage into a temporary folder.
    value = os.environ.get("SKILLREC_DB")
    return Path(value) if value else None


def plan_markdown(result):
    p = result["profile"]
    lines = ["# My skill learning plan", "", f"Education: {p['education']} | Stream: {p['stream']}",
             f"Goal: {p['goal'] or 'Exploring'}", "", *result["notes"], ""]
    for path in result["paths"]:
        lines.extend([f"## {path['track']}", f"Start with: {', '.join(path['ready_skills']) or 'Try the project challenge'}",
                      f"Next steps: {', '.join(path['later_skills']) or 'Build your portfolio'}", f"Project: {path['project']}"])
        for course in path["courses"]:
            lines.append(f"- [{course['title']}]({course['url']}) — {course['provider']} ({course['kind']})")
        lines.append("")
    return "\n".join(lines)


def show_result(result, allow_save=True):
    st.markdown('<div class="eyebrow">YOUR PERSONALISED STARTING POINT</div>', unsafe_allow_html=True)
    st.subheader("A clearer path to your next skill")
    st.caption(f"Plan for {result['profile']['education']} · {result['profile']['stream']}. Change the profile and generate again to update this plan.")
    for note in result["notes"]:
        st.info(note, icon="ℹ️")
    columns = st.columns(3)
    for i, (column, path) in enumerate(zip(columns, result["paths"])):
        with column:
            with st.container(border=True, key=f"path_card_{i}"):
                st.caption("TOP EXPLORATION PATH" if i == 0 else f"ALTERNATIVE {i}")
                st.markdown(f"### {path['track']}")
                st.caption(f"Ranking score {path['score']:.2f} / 1 · not an accuracy or probability")
                st.progress(path["score"])
                st.write("**Skills to start now**")
                if path["ready_skills"]:
                    st.write(" · ".join(path["ready_skills"][:4]))
                else:
                    st.write("You already listed the available foundation skills. Try the project challenge.")
                st.caption("Shared interests: " + (", ".join(path["matched_interests"]) or "No direct match; goal and other features contributed."))
    chosen = st.selectbox("Explore a recommended path", [p["track"] for p in result["paths"]], key="chosen_path")
    path = next(p for p in result["paths"] if p["track"] == chosen)
    course_tab, roadmap_tab, evidence_tab = st.tabs(["Learning courses", "Your next steps", "Why this path?"])
    with course_tab:
        st.caption("Curated demo suggestions. Check the provider's syllabus, level and access terms. Catalogue links are clearly labelled.")
        if not path["courses"]:
            st.success("No additional course in this small catalogue matches your remaining ready skills. Try the project or explore another path.")
        for course in path["courses"]:
            with st.container(border=True, key=f"course_card_{course['id']}"):
                left, right = st.columns([4, 1])
                with left:
                    st.markdown(f"**{course['title']}**")
                    st.caption(f"{course['provider']} · {course['kind']} · {course['level']}")
                    st.write("Explore: " + ", ".join(course["addresses"]))
                    st.caption(course["access"])
                with right:
                    st.link_button("Open resource ↗", course["url"], width="stretch")
    with roadmap_tab:
        st.write("**1 · Build a foundation**")
        st.write(", ".join(path["ready_skills"]) or "Review your current skills with a small practical task.")
        st.write("**2 · Unlock the next step**")
        if path["later_skills"]:
            for skill, prerequisites in path["later_prerequisites"].items():
                st.write(f"{skill}: first practise {', '.join(prerequisites)}.")
        else:
            st.write("Repeat a foundation task independently, then move to a project.")
        st.write("**3 · Make something you can show**")
        st.write(path["project"])
        st.caption("After learning a skill, add it to your current skills and generate a fresh plan.")
    with evidence_tab:
        st.write("**Your inputs used:** education, stream, listed skills, interests and goal words.")
        st.write("Shared skills: " + (", ".join(path["matched_skills"]) or "None yet"))
        st.write("Shared interests: " + (", ".join(path["matched_interests"]) or "None directly"))
        st.write("The ranking combines 35% Decision Tree, 35% KNN and 30% normalised cosine similarity.")
        st.dataframe(pd.DataFrame([{"Method": k, "Contribution input": v} for k, v in path["components"].items()]), hide_index=True, width="stretch")
        st.caption("Component values are model scores. These are broad match explanations, not causal feature attributions. Human-written rules choose skills and courses after the track ranking.")
    a, b, c = st.columns(3)
    with a:
        st.download_button("Download learning plan", plan_markdown(result), "my_learning_plan.md", "text/markdown", width="stretch")
    with b:
        st.download_button("Download full result (JSON)", json.dumps(result, indent=2), "skill_recommendations.json", "application/json", width="stretch")
    with c:
        if allow_save and st.button("Save this plan locally", width="stretch"):
            try:
                save_plan(st.session_state.owner, result, db_path())
                st.success("Saved. Open Saved plans in the sidebar.")
            except (OSError, sqlite3.Error):
                st.error("Could not save to the local folder. You can still download the plan.")
    if allow_save:
        st.caption("Saving is optional. Local plans are visible in this browser session only; download a copy to keep it. No login or cloud sync.")


if "owner" not in st.session_state:
    st.session_state.owner = str(uuid.uuid4())

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-icon">S</span> SkillPath<span class="brand-dot">.</span></div>', unsafe_allow_html=True)
    st.caption("A SMALL STEP. A NEW POSSIBILITY.")
    page = st.radio("Workspace", ["Discover your path", "Saved plans", "Model lab", "Project guide"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Made for every stage**")
    st.caption("Class 10 & 12\n\nDiploma · Undergraduate · Graduate")
    st.markdown('<div class="sidebar-note">YOUR FUTURE, AT YOUR PACE<br><strong>Start curious.<br>Build one skill.</strong></div>', unsafe_allow_html=True)
    st.caption("Academic demo · Synthetic training data")

st.markdown('<div class="topline"><span>STUDENT GROWTH WORKSPACE</span><span class="demo-badge">● Academic demo</span></div>', unsafe_allow_html=True)

revision = (ROOT / "data" / "demo_profiles.json").stat().st_mtime_ns

if page == "Discover your path":
    st.markdown('''<div class="hero"><div class="hero-copy"><div class="eyebrow">DISCOVER • LEARN • GROW</div>
    <h1>Student Skill<br>Recommendation System</h1>
    <p>Turn what you enjoy into what you learn next.<br>A practical skill path, shaped around you.</p>
    <div class="hero-tags"><span>Every education level</span><span>Skills + courses</span><span>A plan you can keep</span></div></div>
    <div class="path-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div>
    <div class="float-card small-card">01 &nbsp; Your interests <b>✦</b></div><div class="float-card main-card"><span>YOUR NEXT CHAPTER</span><strong>Potential → Progress</strong><div class="art-bars"><i></i><i></i><i></i><i></i><i></i></div><small>One skill at a time.</small></div><div class="float-card bottom-card">↗ &nbsp; A path made for you</div></div></div>''', unsafe_allow_html=True)
    left, right = st.columns([2.15, 1], gap="large")
    with left:
        with st.container(border=True, key="profile_card"):
            st.markdown('<div class="eyebrow">01 / YOUR STARTING POINT</div>', unsafe_allow_html=True)
            st.subheader("Tell us a little about you")
            st.caption("No marks or personal details needed. New to skills? Leave current skills empty.")
            if st.button("Try a sample profile", type="secondary"):
                st.session_state.education = "Class 12"
                st.session_state.stream = "Science"
                st.session_state.skills = ["Computer basics"]
                st.session_state.interests = ["Coding", "Websites"]
                st.session_state.goal_choice = "Build websites and apps"
                st.session_state.custom_goal = ""
            with st.form("student_profile"):
                a, b = st.columns(2)
                with a:
                    education = st.selectbox("Education level", EDUCATION, key="education")
                with b:
                    stream = st.selectbox("Stream / field of study", STREAMS, key="stream")
                skills = st.multiselect("Current skills", SKILLS, key="skills", placeholder="What can you already do?")
                interests = st.multiselect("Interests", INTERESTS, key="interests", placeholder="What do you enjoy exploring?")
                goal_choice = st.selectbox("Career goal", ["Still exploring / write my own"] + GOALS, key="goal_choice")
                custom_goal = st.text_input("Your goal in your own words (optional)", max_chars=350, key="custom_goal", placeholder="For example: I want to build useful websites")
                st.caption("Your own words are added to the selected goal. English goal words are supported in this demo.")
                submitted = st.form_submit_button("Find my skill path →", type="primary", width="stretch")
            if submitted:
                goal = ("" if goal_choice.startswith("Still exploring") else goal_choice) + " " + custom_goal.strip()
                profile = {"education": education, "stream": stream, "skills": skills, "interests": interests, "goal": goal.strip()}
                try:
                    st.session_state.result = get_engine(revision).recommend(profile)
                    st.session_state.pop("chosen_path", None)
                except ValueError as error:
                    st.session_state.pop("result", None)
                    st.error(str(error))
    with right:
        st.markdown('''<div class="how-card"><div class="eyebrow">FROM CURIOUS TO CAPABLE</div><h3>Your next step,<br>made simpler.</h3>
        <div class="step"><b>1</b><div><strong>Share your starting point</strong><p>Your education, skills and interests.</p></div></div>
        <div class="step"><b>2</b><div><strong>Explore possible paths</strong><p>Compare skills that fit your goals.</p></div></div>
        <div class="step"><b>3</b><div><strong>Learn something useful</strong><p>Find a resource. Build a small project.</p></div></div></div>
        <div class="tip-card"><span>✦ &nbsp; A NOTE FOR EXPLORERS</span><p>You do not need your whole career figured out. One interest is enough to begin.</p></div>''', unsafe_allow_html=True)
        st.caption("Demonstration only. Recommendations use fictional profiles and a small curated catalogue. Your stream never locks you into a path.")
    if "result" in st.session_state:
        st.divider()
        show_result(st.session_state.result)
    else:
        st.markdown('<div class="empty-strip">✧ &nbsp; Your personalised skills and learning resources will appear here.</div>', unsafe_allow_html=True)

elif page == "Saved plans":
    st.title("Your saved plans")
    st.write("Plans you chose to save during this browser session. Download a copy before closing the session.")
    try:
        plans = list_plans(st.session_state.owner, db_path())
        if not plans:
            st.info("No saved plans yet. Generate a recommendation and choose Save this plan locally.")
        else:
            labels = {p["id"]: f"{p['payload']['paths'][0]['track']} · {p['created_at'][:19]} UTC · {p['id'][:6]}" for p in plans}
            selected = st.selectbox("Choose a saved plan", list(labels), format_func=labels.get)
            show_result(next(p["payload"] for p in plans if p["id"] == selected), allow_save=False)
            if st.button("Delete this session's saved plans", type="secondary"):
                delete_plans(st.session_state.owner, db_path())
                st.rerun()
    except (OSError, sqlite3.Error):
        st.error("Local storage is unavailable. Use downloadable plans from the Discover page.")
    st.caption("This is a local classroom app, without account authentication. Restarting the browser session loses the session token; old records remain on disk until the database is removed. See README privacy notes.")

elif page == "Model lab":
    st.title("How the demo performs")
    st.warning("Synthetic data only. These results measure agreement with fictional labels, not success for real students.")
    st.write("Decision Tree, KNN and cosine prototypes are trained on 75% of unique demo profiles and tested on the other 25%. Preprocessing is fitted on training data only. The app itself uses all demo rows for recommendations.")
    report = get_evaluation(revision)
    a, b, c = st.columns(3)
    a.metric("Training examples", report["train_rows"])
    b.metric("Held-out examples", report["test_rows"])
    c.metric("Duplicate overlap", report["feature_overlap_count"])
    st.dataframe(pd.DataFrame(report["metrics"]).T.rename(columns={"accuracy": "Demo holdout accuracy", "macro_f1": "Macro F1"}), width="stretch")
    st.subheader("Hybrid confusion matrix")
    st.caption("Rows = synthetic reference labels; columns = predicted learning paths.")
    st.dataframe(pd.DataFrame(report["hybrid_confusion_matrix"], index=report["class_order"], columns=report["class_order"]), width="stretch")
    st.subheader("Limits of this evaluation")
    for limitation in report["limitations"]:
        st.write("• " + limitation)
    st.download_button("Download evaluation report", json.dumps(report, indent=2), "evaluation.json", "application/json")

else:
    st.title("Understand and present the project")
    st.write("**Academic working title:** Student Skill Recommendation System Using Machine Learning")
    st.info("The original synopsis PDF was not available in this workspace. This working title and scope follow the supplied request; verify the exact academic title against the synopsis before submission.")
    st.markdown("""**The flow:** Student profile → numerical features → Decision Tree + KNN + cosine ranking → missing skills → curated resources → downloadable plan.

**Decision Tree** learns branching rules from labelled demo profiles. **KNN** compares a profile to seven nearby demo examples. **Cosine Similarity** compares its feature direction to each track's average profile.

**A simple viva explanation:** The system suggests a learning direction from a student's current skills, interests and goals. It identifies skill gaps, checks prerequisites and provides learning resources. Its current training profiles are synthetic, so we demonstrate the software and algorithms without claiming real-world recommendation accuracy.

**How to improve it:** Collect consented profiles, ask teachers or counsellors to label suitable paths independently, evaluate with new students, audit results across education levels and maintain a reviewed course catalogue.
""")
    st.write(f"Available in this demo: **{len(EDUCATION)} education levels · {len(TRACKS)} learning paths · {len(SKILLS)} skills · {len(load_courses())} course/resource entries**.")
    st.caption("Read README.md, docs/PROJECT_GUIDE.md and data/DATA_CARD.md in the downloaded project for setup, code explanations and limitations.")

st.markdown('<div class="footer">SkillPath · Student Skill Recommendation System <span>Learn with purpose. Grow at your pace.</span></div>', unsafe_allow_html=True)
