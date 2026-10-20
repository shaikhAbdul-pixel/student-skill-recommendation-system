# Demo dataset card

## Provenance

**Entirely synthetic.** Generated locally with Python's `random.Random(42)` by `scripts/generate_demo_data.py`. No student records were uploaded, scraped, purchased or surveyed for this dataset. The inaccessible synopsis PDF was not used as a source of training rows.

420 examples: seven tracks × 60 examples, with all five education levels represented within every track. Each track has 12 examples per education level. Streams are drawn independently from the available stream list. This design is for broad app coverage; it is not a population distribution.

## Fields

| Field | Meaning | Used by models? |
|---|---|---|
| `id` | Fictional identifier beginning `DEMO-` | No |
| `source` | `synthetic_demo_v1` provenance label | No |
| `education` | One of the five supported levels | Yes |
| `stream` | Self-described academic field | Yes |
| `skills` | List drawn from the editable skill vocabulary | Yes |
| `interests` | List drawn from the editable interest vocabulary | Yes |
| `goal` | A synthetic English goal sentence, or empty | Yes |
| `track` | Author-intended example learning path | Target label only |

## Generation method

For each track, sample 1–3 related interests and 0–3 related skills. With probability 0.40, append an interest from the entire vocabulary; with probability 0.25, append a skill from the entire vocabulary. With probability 0.18, choose a goal pool from a random track (which can be the original track); independently, omit goal text with probability 0.20. Deduplicate repeated interests/skills. Regenerate if the exact feature dictionary has already appeared.

These are generation probabilities, not asserted observed percentages. Mixing signals intentionally introduces ambiguity; the generating track remains the assigned label. Labels therefore represent the generator's intent, not the only reasonable answer.

Some generated skill combinations may be unrealistic or include a next-step skill without its prerequisites. The app treats reported skills as self-reported; it enforces prerequisites for new recommendations. The dataset is not a model of learning progression.

## Evaluation boundaries

Exact feature duplicates are removed before a seeded stratified 75/25 split. The vocabulary, tree, KNN and track prototypes are fitted only to training data for evaluation. IDs, source strings and target labels are excluded from input. A dummy baseline, accuracy, macro F1 and confusion matrix are reported.

The same generation templates and topic vocabulary occur in both subsets. A random split does not eliminate that synthetic design bias. High scores reflect recovery of those patterns, not evidence that recommended careers or courses are right for real people. No protected demographic attributes are collected, and fairness has not been evaluated.

## Resource catalogue

`courses.json` is a human-curated list of official provider links and editorial skill mappings, not a learned dataset. A resource may be a tutorial, book, library or discovery catalogue. Discovery mappings are **search topics**, not a statement that a single course teaches all mapped skills. Links are checked for page availability; current syllabus, enrolment terms, certificates and completion requirements must be reviewed on the provider site. No durations or employment outcomes are asserted.

## Replacing demo data

Keep the JSON schema but store real consented data separately. Validate list values against `catalog.py`, retain provenance, remove personal identifiers and duplicates, and independently review target labels. Update the data card and evaluation method. Do not simply relabel synthetic rows as real records. Evaluation currently assumes enough examples per class for stratified splitting and a catalogue entry for each target class; a new dataset requires schema and class-count checks before use.
