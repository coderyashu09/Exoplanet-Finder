"""Dataset Audit and Inspection Script for NASA Kepler DR24 TCE Data."""
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure root in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg


def inspect_dataset(file_path: Path) -> dict:
    """Perform detailed audit of a TCE dataset file."""
    print("=" * 70)
    print(f"AUDITING DATASET: {file_path.name}")
    print(f"Full path: {file_path}")
    print("=" * 70)

    if not file_path.exists():
        print(f"ERROR: Dataset file not found at {file_path}")
        return {"status": "missing", "path": str(file_path)}

    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")

    df = pd.read_csv(file_path, comment="#")
    total_rows = len(df)
    total_cols = len(df.columns)
    unique_stars = df["kepid"].nunique() if "kepid" in df.columns else 0

    print(f"Total rows: {total_rows}")
    print(f"Total columns: {total_cols}")
    print(f"Unique Kepler stars (kepid): {unique_stars}")

    # Column inspection
    columns_info = {}
    missing_summary = {}
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        missing_summary[col] = {
            "null_count": null_count,
            "null_pct": round(null_count / total_rows * 100, 2),
            "dtype": str(df[col].dtype),
        }

    print("\nKey Orbital Columns Check:")
    key_cols = ["kepid", "tce_plnt_num", "tce_period", "tce_time0bk", "tce_duration", "tce_depth"]
    for col in key_cols:
        if col in df.columns:
            min_val = float(df[col].min()) if pd.api.types.is_numeric_dtype(df[col]) else "N/A"
            max_val = float(df[col].max()) if pd.api.types.is_numeric_dtype(df[col]) else "N/A"
            print(f"  - {col}: present, range [{min_val}, {max_val}], nulls: {missing_summary[col]['null_count']}")
        else:
            print(f"  - {col}: MISSING")

    # Label column check
    label_status = {}
    if "av_training_set" in df.columns:
        counts = df["av_training_set"].value_counts(dropna=False).to_dict()
        label_status["av_training_set"] = {str(k): int(v) for k, v in counts.items()}
        print("\nLabel Column 'av_training_set' found:")
        for k, v in counts.items():
            print(f"  {k}: {v}")
    else:
        print("\nWARNING: 'av_training_set' is NOT present in this CSV file!")
        print("Note: The file contains Kepler orbital parameters but requires labels from NASA TAP service.")

    # Autovetter check (leakage audit)
    leakage_cols = [c for c in df.columns if c.startswith("av_pp_") or c == "av_pred_class"]
    print(f"\nAutovetter Prediction Columns Present (Potential Leakage): {leakage_cols}")

    report = {
        "file_name": file_path.name,
        "file_size_mb": round(file_size_mb, 2),
        "total_rows": total_rows,
        "total_columns": total_cols,
        "unique_stars": unique_stars,
        "columns": df.columns.tolist(),
        "key_columns_present": [c for c in key_cols if c in df.columns],
        "label_distribution": label_status,
        "leakage_columns": leakage_cols,
        "missing_summary": missing_summary,
    }

    output_path = cfg.metrics_dir / "dataset_audit.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nAudit report saved to: {output_path}")
    print("=" * 70)
    return report


if __name__ == "__main__":
    target = cfg.original_data_file
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    inspect_dataset(target)

