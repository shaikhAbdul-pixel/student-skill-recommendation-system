# Build validation

Verified locally on **20 October 2026** using Python 3.10.3, Streamlit 1.54.0, scikit-learn 1.7.2, pandas 2.3.3 and NumPy 2.2.6.

## Automated checks

`python -m unittest discover -v` — **12 tests passed**, including the actual Streamlit entrypoint via AppTest. Tests cover all five education levels, goal/interest changes, beginners, current skills, prerequisite gating, empty/unsupported inputs, catalogue consistency, seeded data regeneration, held-out evaluation integrity, local database isolation and the UI generate/save/delete/navigation flow.

`python -m compileall -q app.py src scripts tests` — passed.

`python scripts/evaluate.py` — completed and wrote `evaluation.json`. 420 unique synthetic records, 315 training, 105 held out, zero exact feature overlap. Full metric values, confusion matrix, per-class report, dataset hash and runtime versions are included in that JSON. Evaluation is limited to synthetic design patterns.

Streamlit AppTest emits a harmless missing-script-context warning when launched through the test runner; there were no app exceptions in the tests.

## Browser checks

The actual Streamlit server was launched on localhost and its page loaded in a browser. A sample Class 12 profile produced Software Development as the leading path, ready skills, alternatives, prerequisite-aware next steps and working resource link elements. The empty form displayed a validation message. The JSON download button produced a file, which was parsed and checked against the sample profile; a copy is included as `sample_recommendations.json`. The interface was visually reviewed at a 1440 × 1000 desktop viewport and 390 × 844 phone viewport, as well as the default narrower desktop panel. The viewport override was reset after inspection. Screenshots are in `docs/screenshots/`.

Local app generation and save/delete flows were tested. External provider pages were checked separately as sources; course enrolment, certificates and third-party account flows were not tested. Setup scripts are conveniences; dependencies were verified in the installed runtime rather than on a clean operating system. No public hosting deployment was performed.

## Outstanding source verification

The referenced synopsis PDF and previous UI image were unavailable. The exact original academic title and paragraph-by-paragraph synopsis alignment have **not** been verified. The README and project guide mark the supplied academic title as a working title.
