"""Experiment Tracking Center router."""
import json
import sqlite3
from typing import Dict, Any, List
from fastapi import APIRouter

from src.config import cfg

router = APIRouter(prefix="/api/experiments", tags=["Experiments"])


@router.get("")
def list_experiments() -> List[Dict[str, Any]]:
    db_path = cfg.experiments_db
    if not db_path.exists():
        return []

    results: List[Dict[str, Any]] = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiments ORDER BY timestamp DESC")
        rows = cursor.fetchall()

        for r in rows:
            item = dict(r)
            # Parse parameters_json and metrics_json
            if item.get("parameters_json"):
                try:
                    item["parameters"] = json.loads(item["parameters_json"])
                except Exception:
                    item["parameters"] = {}
            if item.get("metrics_json"):
                try:
                    item["metrics"] = json.loads(item["metrics_json"])
                except Exception:
                    item["metrics"] = {}
            results.append(item)
        conn.close()
    except Exception:
        pass

    return results

