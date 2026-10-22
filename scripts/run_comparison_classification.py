"""Reuse the two-round runner with a new evidence directory; preserve 4.6 archives."""

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "doctor_trial_runner", ROOT / "scripts/run_doctor_trial_quality.py"
)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
batch.OUTPUT = ROOT / "evaluations/reports/comparison-classification-4.7/live"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--closure", action="store_true")
    args = parser.parse_args()
    if args.final:
        batch.OUTPUT = ROOT / "evaluations/reports/comparison-classification-4.7/live-final"
    if args.release:
        batch.OUTPUT = ROOT / "evaluations/reports/comparison-classification-4.7/live-release"
    if args.closure:
        batch.OUTPUT = ROOT / "evaluations/reports/comparison-classification-4.7/live-closure"
    batch.run()
