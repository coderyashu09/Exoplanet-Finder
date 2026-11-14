"""Experiment tracker for training runs using SQLite database and JSON serialization."""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd

from src.config import cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ExperimentTracker:
    """Manages experiment persistence and history using a local SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or cfg.experiments_db
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        """Create experiments table if it does not already exist."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    dataset_version TEXT NOT NULL,
                    random_seed INTEGER NOT NULL,
                    training_duration REAL NOT NULL,
                    best_val_auc REAL,
                    test_auc REAL,
                    average_precision REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    specificity REAL,
                    threshold REAL,
                    parameters_json TEXT,
                    model_path TEXT,
                    notes TEXT
                )
                """
            )
            conn.commit()

    def log_experiment(
        self,
        experiment_id: str,
        model_type: str,
        training_duration: float,
        best_val_auc: Optional[float],
        test_metrics: Dict[str, Any],
        parameters: Dict[str, Any],
        model_path: str,
        model_version: str = "1.0.0",
        dataset_version: str = "DR24",
        random_seed: int = 42,
        notes: str = "",
    ) -> None:
        """Record a completed training experiment into SQLite database."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO experiments (
                    experiment_id, timestamp, model_type, model_version, dataset_version,
                    random_seed, training_duration, best_val_auc, test_auc, average_precision,
                    precision, recall, f1_score, specificity, threshold, parameters_json,
                    model_path, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    now_str,
                    model_type,
                    model_version,
                    dataset_version,
                    random_seed,
                    round(training_duration, 2),
                    best_val_auc,
                    test_metrics.get("roc_auc"),
                    test_metrics.get("average_precision"),
                    test_metrics.get("precision"),
                    test_metrics.get("recall"),
                    test_metrics.get("f1_score"),
                    test_metrics.get("specificity"),
                    test_metrics.get("threshold"),
                    json.dumps(parameters),
                    str(model_path),
                    notes,
                ),
            )
            conn.commit()
        logger.info(f"Logged experiment {experiment_id} successfully.")

    def get_all_experiments(self) -> pd.DataFrame:
        """Retrieve all experiment runs as a pandas DataFrame."""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM experiments ORDER BY timestamp DESC", conn)
        return df

    def get_experiment_by_id(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full details of a specific experiment."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [col[0] for col in cursor.description]
            result = dict(zip(cols, row))
            if result.get("parameters_json"):
                result["parameters"] = json.loads(result["parameters_json"])
            return result

