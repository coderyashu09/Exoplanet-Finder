"""Configuration loader and path manager for Exoplanet Finder."""
from pathlib import Path
from typing import Any, Dict
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


def load_raw_config() -> Dict[str, Any]:
    """Load configuration from config.yaml."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class Config:
    """Central configuration class with resolved Path objects."""

    def __init__(self, raw: Dict[str, Any] = None):
        if raw is None:
            raw = load_raw_config()
        self._raw = raw

        # Project Info
        self.project_name = raw.get("project", {}).get("name", "Exoplanet Finder")
        self.project_tagline = raw.get("project", {}).get("tagline", "")
        self.project_version = raw.get("project", {}).get("version", "1.0.0")

        # Paths
        paths = raw.get("paths", {})
        self.raw_data_dir = PROJECT_ROOT / paths.get("raw_data_dir", "Data/raw")
        self.original_data_file = PROJECT_ROOT / paths.get(
            "original_data_file", "Data/q1_q17_dr24_tce_2026.11.05_23.02.25.csv"
        )
        self.tce_catalog_file = PROJECT_ROOT / paths.get(
            "tce_catalog_file", "Data/raw/q1_q17_dr24_tce.csv"
        )
        self.lightcurves_dir = PROJECT_ROOT / paths.get("lightcurves_dir", "Data/lightcurves")
        self.processed_dir = PROJECT_ROOT / paths.get("processed_dir", "Data/processed")
        self.splits_dir = PROJECT_ROOT / paths.get("splits_dir", "Data/splits")

        self.models_dir = PROJECT_ROOT / paths.get("models_dir", "models")
        self.checkpoints_dir = PROJECT_ROOT / paths.get("checkpoints_dir", "models/checkpoints")
        self.baseline_dir = PROJECT_ROOT / paths.get("baseline_dir", "models/baseline")
        self.metadata_dir = PROJECT_ROOT / paths.get("metadata_dir", "models/metadata")

        self.outputs_dir = PROJECT_ROOT / paths.get("outputs_dir", "outputs")
        self.metrics_dir = PROJECT_ROOT / paths.get("metrics_dir", "outputs/metrics")
        self.figures_dir = PROJECT_ROOT / paths.get("figures_dir", "outputs/figures")
        self.predictions_dir = PROJECT_ROOT / paths.get("predictions_dir", "outputs/predictions")
        self.experiments_dir = PROJECT_ROOT / paths.get("experiments_dir", "outputs/experiments")
        self.experiments_db = PROJECT_ROOT / paths.get(
            "experiments_db", "outputs/experiments/experiments.db"
        )

        # Data
        data = raw.get("data", {})
        self.label_column = data.get("label_column", "av_training_set")
        self.valid_labels = data.get("valid_labels", {"PC": 1, "AFP": 0, "NTP": 0})
        self.excluded_labels = data.get("excluded_labels", ["UNK"])
        self.star_id_col = data.get("star_id_col", "kepid")
        self.train_split = data.get("train_split", 0.80)
        self.val_split = data.get("val_split", 0.10)
        self.test_split = data.get("test_split", 0.10)
        self.random_seed = data.get("random_seed", 42)
        self.time_system = data.get("time_system", "BKJD")

        # Preprocessing
        prep = raw.get("preprocessing", {})
        self.flatten_window_length = prep.get("flatten_window_length", 401)
        self.polyorder = prep.get("polyorder", 2)
        self.transit_mask_factor = prep.get("transit_mask_factor", 1.2)
        self.global_bins = prep.get("global_bins", 2001)
        self.local_bins = prep.get("local_bins", 201)
        self.local_duration_factor = prep.get("local_duration_factor", 4.0)
        self.min_valid_flux_ratio = prep.get("min_valid_flux_ratio", 0.5)

        # Baseline
        base = raw.get("baseline", {})
        self.baseline_model_type = base.get("model_type", "HistGradientBoostingClassifier")
        self.baseline_features = base.get(
            "features", ["tce_period", "tce_duration", "tce_depth"]
        )
        self.baseline_random_state = base.get("random_state", 42)
        self.baseline_max_iter = base.get("max_iter", 200)
        self.baseline_learning_rate = base.get("learning_rate", 0.05)
        self.baseline_max_leaf_nodes = base.get("max_leaf_nodes", 31)

        # CNN
        cnn = raw.get("cnn", {})
        self.cnn_global_length = cnn.get("global_length", 2001)
        self.cnn_local_length = cnn.get("local_length", 201)
        self.cnn_global_channels = cnn.get("global_channels", [16, 32, 64, 128])
        self.cnn_local_channels = cnn.get("local_channels", [16, 32, 64, 128])
        self.cnn_dense_units = cnn.get("dense_units", [512, 128])
        self.cnn_dropout = cnn.get("dropout", 0.3)
        self.cnn_learning_rate = cnn.get("learning_rate", 0.001)
        self.cnn_weight_decay = cnn.get("weight_decay", 0.0001)
        self.cnn_batch_size = cnn.get("batch_size", 32)
        self.cnn_epochs = cnn.get("epochs", 50)
        self.cnn_early_stopping_patience = cnn.get("early_stopping_patience", 10)
        self.cnn_device = cnn.get("device", "auto")
        self.cnn_pos_weight = cnn.get("pos_weight", 1.0)

        # Inference
        inf = raw.get("inference", {})
        self.default_threshold = inf.get("default_threshold", 0.50)
        self.uncertainty_window = inf.get("uncertainty_window", 0.15)
        self.kepler90_kepid = inf.get("kepler90_kepid", 11442793)

    def ensure_directories(self) -> None:
        """Create all necessary application directories if they do not exist."""
        for p in [
            self.raw_data_dir,
            self.lightcurves_dir,
            self.processed_dir,
            self.splits_dir,
            self.models_dir,
            self.checkpoints_dir,
            self.baseline_dir,
            self.metadata_dir,
            self.outputs_dir,
            self.metrics_dir,
            self.figures_dir,
            self.predictions_dir,
            self.experiments_dir,
        ]:
            p.mkdir(parents=True, exist_ok=True)


# Global singleton instance
cfg = Config()
cfg.ensure_directories()

