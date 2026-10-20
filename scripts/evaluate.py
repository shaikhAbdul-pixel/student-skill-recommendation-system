"""Run from the project folder: python scripts/evaluate.py"""
import json
import platform
import sys
from pathlib import Path
import sklearn
import streamlit
import numpy
import pandas

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.catalog import ROOT
from src.engine import load_profiles
from src.evaluation import evaluate

if __name__ == "__main__":
    report = evaluate(load_profiles())
    report["runtime"] = {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                         "streamlit": streamlit.__version__, "numpy": numpy.__version__, "pandas": pandas.__version__}
    target = ROOT / "reports" / "evaluation.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("SYNTHETIC DEMO HOLDOUT ONLY - not validated on real students")
    print(f"Train: {report['train_rows']}; test: {report['test_rows']}; duplicate overlap: {report['feature_overlap_count']}")
    for model, metrics in report["metrics"].items():
        print(f"{model:25} Accuracy: {metrics['accuracy']:.3f}  Macro F1: {metrics['macro_f1']:.3f}")
    print(f"Full report: {target}")
