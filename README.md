# Student Skill Recommendation System Using Machine Learning

**UI header: Student Skill Recommendation System**

**Open the running app:** [student-skill-path.streamlit.app](https://student-skill-path.streamlit.app/)

The GitHub page contains source code. Use the app link above to run the model in your browser. It is hosted on Streamlit Community Cloud and does not require the author\'s computer to remain on. Cloud runtime: Python 3.11; repository branch `main`; entrypoint `app.py`. Free hosting can sleep when idle; reopen the same URL to wake it.

A runnable Python academic demonstration with a blue-and-white Streamlit interface, scikit-learn Decision Tree, KNN, cosine similarity, skill-gap recommendations, curated learning resources, optional local SQLite saving and downloadable plans.

[Desktop preview](docs/screenshots/app-desktop.jpg) · [Phone preview](docs/screenshots/app-mobile.jpg) · [Viva and code guide](docs/PROJECT_GUIDE.md)

**Source alignment:** The request refers to `AnsariMehrishAnam_245124.pdf` in an earlier ChatGPT chat. That PDF and the earlier UI image were not accessible during this build. The academic title above is a **working title**, not a verified transcription. This implementation follows the explicit requirements in the current request. Verify the exact synopsis title and any additional requirements before academic submission. The design is an original interpretation of the requested blue-and-white style.

## Run locally

Extract the ZIP first. Install **Python 3.10 or 3.11** (the supplied dependency versions were tested on Python 3.10.3). Open a terminal **inside this project folder**, where `app.py` is located.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Alternatively, double-click `setup_windows.bat` once, then `run_windows.bat`. Setup downloads dependencies and needs internet. If `python` is unavailable, install Python with “Add Python to PATH”, then reopen the terminal. These scripts do not need administrator rights.

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Open **http://localhost:8501** if your browser does not open automatically. Stop with **Ctrl+C** in the terminal. No API key, login or external database server is needed. The app works offline after dependencies are installed; opening external learning resources requires internet. If port 8501 is busy, add `--server.port 8502` and visit that port instead.

## Try the application

1. Click **Try a sample profile**, then **Find my skill path**.
2. Or choose Class 10, Class 12, Diploma, Undergraduate or Graduate, then a stream and your skills/interests/goals. Leave skills empty if you are a beginner. “General / Not decided” is available for streams.
3. Compare three possible learning paths. Explore their courses, next steps and explanation tabs.
4. Download your plan as Markdown or the complete result as JSON. Click **Save this plan locally** only if you want a local database copy.
5. Open **Model lab** to inspect real, reproducible demo evaluation results. **Project guide** explains the project for a presentation.

Goal text uses simple **English token matching**, not an LLM. You can combine a suggested goal with your own words. Unsupported free text alone produces a useful message instead of an arbitrary recommendation. Select a listed interest to explore a new goal. Scores compare the seven supported paths; they do not measure aptitude or eligibility. Every education level can explore every path. Prerequisites are based on listed skills, not on degree status.

## What each algorithm actually does

| Step | Implementation |
|---|---|
| Input features | Education and stream one-hot features (weight 0.3); multi-hot skills (0.7), interests (1.0), unique goal words (0.65). Row-wise L2 normalisation. |
| Decision Tree | `DecisionTreeClassifier(max_depth=6, min_samples_leaf=3, random_state=42)` predicts a broad learning path. |
| KNN | Seven neighbours, cosine distance, brute-force search and distance-weighted class voting. |
| Cosine Similarity | Compares the profile to the average training feature vector of each learning path; similarities are normalised across paths. |
| Hybrid ranking | `0.35 × tree + 0.35 × KNN + 0.30 × normalised cosine`. These are documented design weights, not optimised weights. |
| Skills | Human-written ordered path lists minus existing skills, with prerequisite checks. |
| Courses | Human-curated resource-to-skill mappings, filtered by ready skills and listed prerequisites. No model predicts course completion or student outcomes. |
| Persistence | SQLite stores JSON plans only after Save. Downloads require no database. |

The models are trained in memory on startup, with Streamlit caching. There is no pre-trained binary to trust or rebuild. The running app fits all demo data; evaluation separately fits a model on training data only.

## Honest data and evaluation

`data/demo_profiles.json` contains **420 fictional, seeded examples**, 60 for each of seven paths. It contains no actual student names, marks, contact details, surveyed answers, placement outcomes or employer data. Labels express the generator author's intended example path, not independently verified truth. See [DATA_CARD.md](data/DATA_CARD.md).

The fixed 75/25 stratified holdout contains **315 training / 105 test rows**, with **zero exact feature duplicates across the split**. Vocabulary and all models are fitted on training rows only. The included report from the tested runtime is:

| Method | Synthetic holdout accuracy | Macro F1 |
|---|---:|---:|
| Decision Tree | 53.33% | 0.569 |
| KNN | 97.14% | 0.971 |
| Cosine Similarity | 97.14% | 0.971 |
| Hybrid | 97.14% | 0.971 |
| Most-frequent baseline | 14.29% | 0.036 |

**These numbers are not real-world recommendation accuracy.** Synthetic profiles reuse small sets of topic-specific phrases and interests; recovering those patterns is much easier than judging a real student's best learning path. The hybrid does not outperform KNN in this split. This evaluation does not measure course quality, learning gains, fairness or employability. The shallow tree underfits some paths. A single split does not establish uncertainty or generalisation. No production accuracy is claimed.

To reproduce:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate.py
.\.venv\Scripts\python.exe -m unittest discover -v
```

Use `.venv/bin/python` on macOS/Linux. Evaluation writes `reports/evaluation.json`: confusion matrix, per-class precision/recall/F1, baseline, dataset hash, runtime versions and limitations. The **12 automated tests** cover all education levels, meaningful profile changes, empty/unknown inputs, skill gaps and prerequisites, catalogue consistency, deterministic synthetic generation, evaluation integrity, SQLite session isolation, and UI generation/save/delete/navigation. Streamlit AppTest exercises the actual app entrypoint. Tests do not fetch external course pages.

To regenerate the same demo data after editing the generator:

```bash
python scripts/generate_demo_data.py
python scripts/evaluate.py
python -m unittest discover -v
```

If you use a virtual environment, substitute its Python path. Rerun evaluation before tests after changing the dataset because a test checks the saved report against the current data. Restart the running app after changing Python code or catalogue files if results appear stale.

## Project structure

```text
app.py                       Streamlit screens, widgets, downloads
assets/style.css             Responsive blue-and-white styling
.streamlit/config.toml       Theme, cloud-compatible server settings, telemetry preference
src/catalog.py               Education/stream options, paths and prerequisites
src/profiles.py              Input validation and readable feature conversion
src/engine.py                Decision Tree, KNN, cosine ranking and skill gaps
src/storage.py               Parameterised SQLite save/list/delete functions
src/evaluation.py            Leakage-aware synthetic holdout evaluation
data/demo_profiles.json      Clearly marked fictional student examples
data/courses.json            Editable learning resource catalogue
data/DATA_CARD.md            Generation method, schema and limitations
scripts/generate_demo_data.py Rebuild demo examples with seed 42
scripts/evaluate.py          Reproduce metrics and write the full report
tests/test_system.py         Behaviour, storage and Streamlit integration tests
reports/evaluation.json      Generated evaluation evidence
reports/VALIDATION.md        Recorded verification and practical limits
docs/PROJECT_GUIDE.md        Architecture, viva notes and extension guide
docs/SOURCES.md              Official technical and learning-resource links
local_data/plans.sqlite3     Created only at runtime; excluded from the ZIP
```

## Local storage and privacy

No profile is automatically added to training data. Save writes the profile and result to an unencrypted SQLite file in `local_data/`. A random server-side session token restricts the Saved plans screen to plans from the current Streamlit browser session. It is **not account authentication**. Closing/reconnecting a browser may create a new session; previous records stay on disk but are no longer available through the new session's Saved plans screen. Download a copy for durable access. Delete the current session's records with the button on Saved plans; after stopping the app, remove `local_data/plans.sqlite3` to erase all stored plans. Do not store sensitive details in goal text.

The public cloud deployment is an academic demo using synthetic training data. It has no account authentication; avoid entering sensitive information. SQLite files on free cloud hosting are not durable storage and can disappear on a rebuild or restart, so download plans you want to keep. A production service would require authentication, retention controls, encrypted storage, reviewed privacy practices and an independently validated dataset.

## Known limits and next work

Seven broad example tracks and a small manually maintained resource catalogue are not comprehensive career guidance. Education and stream provide weak context; existing skills and interests are self-reported. The feature weights do not guarantee fairness. Resource levels and prerequisites are editorial simplifications. Some entries are libraries or discovery catalogues rather than individual courses, and are labelled accordingly. No prices, durations, certificate guarantees or placement promises are invented. Provider links were checked on 20 October 2026; some require JavaScript or an account and full enrolment was not tested.

For a stronger research project: collect consented representative profiles, obtain multiple independent expert recommendations, agree on evaluation criteria, hold out entirely new students, compare methods and measure ranking relevance and learning outcomes. Report results by education level, and review skill/course mappings with teachers. Keep the synthetic demo dataset separate from any future real data.

Original code and synthetic examples are supplied under the MIT licence. External learning resources remain subject to their providers' terms.
