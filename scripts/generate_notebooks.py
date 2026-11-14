"""Generate professional Jupyter research notebooks."""
import json
from pathlib import Path


def make_nb(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.12"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code_cell(code):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": code.splitlines(keepends=True)}


def main():
    nb1 = make_nb([
        md_cell("# 01 — NASA Kepler DR24 TCE Data Exploration\nInitial exploratory data analysis on Kepler Q1-Q17 DR24 Threshold Crossing Events."),
        code_cell("import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path.cwd().parent))\n\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nfrom src.config import cfg\nfrom src.data_loader import get_or_build_tce_catalog, clean_and_filter_tce_data"),
        code_cell("df_raw = get_or_build_tce_catalog()\nprint('Total raw records:', len(df_raw))\ndf_raw.head()"),
        code_cell("df_clean, audit = clean_and_filter_tce_data(df_raw)\nprint('Cleaned records:', len(df_clean))\nprint('Unique Kepler stars:', df_clean['kepid'].nunique())\nprint(df_clean['av_training_set'].value_counts())"),
        code_cell("fig, axes = plt.subplots(1, 3, figsize=(15, 4))\ndf_clean['tce_period'].hist(bins=50, ax=axes[0], log=True, color='#63B3FF')\naxes[0].set_title('Orbital Period [days]')\ndf_clean['tce_duration'].hist(bins=50, ax=axes[1], color='#35D49A')\naxes[1].set_title('Transit Duration [hrs]')\ndf_clean['tce_depth'].hist(bins=50, ax=axes[2], log=True, color='#FFBE55')\naxes[2].set_title('Transit Depth [ppm]')\nplt.tight_layout()\nplt.show()"),
    ])

    nb2 = make_nb([
        md_cell("# 02 — Stellar Light Curve Processing & Phase Folding\nPhotometry retrieval, transit masking, Savitzky-Golay detrending, and dual-view generation."),
        code_cell("import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path.cwd().parent))\n\nimport numpy as np\nimport matplotlib.pyplot as plt\nfrom src.config import cfg\nfrom src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve\nfrom src.preprocessing import validate_and_align_time_system, flatten_lightcurve\nfrom src.phase_folding import generate_two_views"),
        code_cell("cache = LightCurveCache()\ntime_arr, flux_arr, flux_err, meta = download_stellar_lightcurve(11442793, cache=cache)\nprint(f'Loaded {len(time_arr)} cadences for Kepler-90 across {meta.get(\"quarters\")} quarters.')"),
        code_cell("t_clean = validate_and_align_time_system(time_arr)\nflat_flux, trend, f_meta = flatten_lightcurve(t_clean, flux_arr, period=14.449, t0=133.0, duration_hours=3.5)\nglobal_v, local_v, v_meta = generate_two_views(t_clean, flat_flux, period=14.449, t0=133.0, duration_hours=3.5)\nprint('Global View Shape:', global_v.shape)\nprint('Local View Shape:', local_v.shape)"),
        code_cell("fig, axes = plt.subplots(1, 2, figsize=(14, 4))\naxes[0].plot(global_v, color='#63B3FF', lw=1)\naxes[0].set_title('Global View (2001 bins)')\naxes[1].plot(local_v, color='#35D49A', lw=1.5)\naxes[1].set_title('Local View (201 bins)')\nplt.tight_layout()\nplt.show()"),
    ])

    nb3 = make_nb([
        md_cell("# 03 — Model Experiments: Baseline vs Two-View CNN\nCompares tabular HistGradientBoosting baseline against Two-View 1D Convolutional Neural Network."),
        code_cell("import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path.cwd().parent))\n\nimport pandas as pd\nimport torch\nfrom src.config import cfg\nfrom src.baseline import BaselinePipeline\nfrom src.model import DualViewExoplanetCNN"),
        code_cell("df_train = pd.read_csv(cfg.processed_dir / 'tce_train.csv')\ndf_val = pd.read_csv(cfg.processed_dir / 'tce_val.csv')\ndf_test = pd.read_csv(cfg.processed_dir / 'tce_test.csv')\nprint(f'Train: {len(df_train)}, Val: {len(df_val)}, Test: {len(df_test)}')"),
        code_cell("base_pipe = BaselinePipeline()\nval_metrics = base_pipe.train(df_train, df_val)\ntest_metrics = base_pipe.evaluate(df_test)\nprint('Baseline Test Metrics:', test_metrics['metrics'])"),
        code_cell("model = DualViewExoplanetCNN()\nprint(model.count_parameters())\nx_g = torch.randn(2, 1, 2001)\nx_l = torch.randn(2, 1, 201)\nout = model.predict_proba(x_g, x_l)\nprint('Sample Output shape:', out.shape)"),
    ])

    nb4 = make_nb([
        md_cell("# 04 — Model Evaluation & Explainability Analysis\nComprehensive test set evaluation, grouped bootstrap confidence intervals, and Integrated Gradients feature attribution."),
        code_cell("import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path.cwd().parent))\n\nimport json\nimport pandas as pd\nfrom src.config import cfg\nfrom src.evaluate import compare_models, analyze_false_positives_and_negatives"),
        code_cell("b_path = cfg.metrics_dir / 'baseline_metrics.json'\nif b_path.exists():\n    print(json.dumps(json.load(open(b_path)), indent=2))"),
        code_cell("df_test = pd.read_csv(cfg.processed_dir / 'tce_test.csv')\nprint(f'Test set contains {len(df_test)} TCE candidates across {df_test[\"kepid\"].nunique()} unique stars.')"),
    ])

    Path("notebooks/01_data_exploration.ipynb").write_text(json.dumps(nb1, indent=1), encoding="utf-8")
    Path("notebooks/02_lightcurve_analysis.ipynb").write_text(json.dumps(nb2, indent=1), encoding="utf-8")
    Path("notebooks/03_model_experiments.ipynb").write_text(json.dumps(nb3, indent=1), encoding="utf-8")
    Path("notebooks/04_model_evaluation.ipynb").write_text(json.dumps(nb4, indent=1), encoding="utf-8")
    print("All 4 Jupyter notebooks successfully generated.")


if __name__ == "__main__":
    main()

