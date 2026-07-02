"""Run the full local MLOps pipeline in sequence."""

from __future__ import annotations

import subprocess
import sys


PIPELINE_STEPS = [
    (
        "[1/5] Running data ingestion...",
        "[1/5] Data ingestion completed.",
        ["-m", "src.data.ingest"],
    ),
    (
        "[2/5] Running data profiling...",
        "[2/5] Data profiling completed.",
        ["-m", "src.data.profile"],
    ),
    (
        "[3/5] Running data validation...",
        "[3/5] Data validation completed.",
        ["-m", "src.data.validate"],
    ),
    (
        "[4/5] Running data preprocessing...",
        "[4/5] Data preprocessing completed.",
        ["-m", "src.data.preprocess"],
    ),
    (
        "[5/5] Running model training...",
        "[5/5] Model training completed.",
        ["-m", "src.training.train"],
    ),
]


def run_pipeline() -> None:
    """Execute the local pipeline step by step and stop on the first failure."""
    for start_message, success_message, module_args in PIPELINE_STEPS:
        print(start_message)
        subprocess.run([sys.executable, *module_args], check=True)
        print(success_message)

    print("Local MLOps pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
