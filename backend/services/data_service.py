"""
Data service for loading, validating, persisting, and managing incident datasets.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import logging
import re
import csv

from backend.config import DATA_FILE, DYNAMIC_DATA_FILE, ALLOWED_CATEGORIES, ALLOWED_SEVERITIES

logger = logging.getLogger(__name__)


class DataService:
    """
    Manages loading, validation, and persistent storage of incident records.
    Preserves original reference dataset unchanged while persisting live user submissions
    to a dynamic data file that survives server restarts.
    """

    def __init__(self, csv_path: Optional[Path] = None, dynamic_path: Optional[Path] = None):
        self.csv_path = csv_path or DATA_FILE
        self.dynamic_path = dynamic_path or DYNAMIC_DATA_FILE
        self._baseline_records: List[Dict[str, Any]] = []
        self._records: List[Dict[str, Any]] = []
        self._is_loaded: bool = False
        self._validation_errors: List[str] = []
        self.load_data()

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Loads baseline reference dataset, followed by any persisted dynamic records.
        """
        self._records = []
        self._baseline_records = []
        self._validation_errors = []

        if not self.csv_path.exists():
            msg = f"Dataset file not found at path: {self.csv_path}"
            logger.error(msg)
            self._validation_errors.append(msg)
            self._is_loaded = False
            return []

        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            msg = f"Failed to parse CSV file: {e}"
            logger.error(msg)
            self._validation_errors.append(msg)
            self._is_loaded = False
            return []

        if df.empty:
            msg = "Dataset CSV is empty."
            logger.warning(msg)
            self._validation_errors.append(msg)
            self._is_loaded = False
            return []

        # Validate required columns
        required_cols = {"incident_id", "narrative", "target_category", "target_severity"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            msg = f"Dataset is missing required columns: {missing_cols}"
            logger.error(msg)
            self._validation_errors.append(msg)
            self._is_loaded = False
            return []

        seen_ids = set()
        cleaned_baseline = []

        for idx, row in df.iterrows():
            incident_id = str(row["incident_id"]).strip() if pd.notna(row["incident_id"]) else f"REC_{idx+1:03d}"
            narrative = str(row["narrative"]).strip() if pd.notna(row["narrative"]) else ""

            if not narrative:
                self._validation_errors.append(f"Row {idx}: missing narrative, skipping.")
                continue

            if incident_id in seen_ids:
                new_id = f"{incident_id}_dup{idx}"
                self._validation_errors.append(f"Row {idx}: duplicate ID '{incident_id}' renamed to '{new_id}'.")
                incident_id = new_id

            seen_ids.add(incident_id)

            category = str(row["target_category"]).strip().lower() if pd.notna(row["target_category"]) else "unknown"
            if category not in ALLOWED_CATEGORIES:
                self._validation_errors.append(f"Row {idx}: invalid category '{category}', flagging as unknown.")
                category = "unknown"

            severity = str(row["target_severity"]).strip().lower() if pd.notna(row["target_severity"]) else "low"
            if severity not in ALLOWED_SEVERITIES:
                self._validation_errors.append(f"Row {idx}: invalid severity '{severity}', defaulting to medium.")
                severity = "medium"

            cleaned_baseline.append({
                "incident_id": incident_id,
                "narrative": narrative,
                "target_category": category,
                "target_severity": severity
            })

        self._baseline_records = list(cleaned_baseline)
        all_records = list(cleaned_baseline)

        # Load persisted dynamic records if file exists
        if self.dynamic_path and self.dynamic_path.exists():
            try:
                dyn_df = pd.read_csv(self.dynamic_path)
                for idx, row in dyn_df.iterrows():
                    d_id = str(row["incident_id"]).strip() if pd.notna(row.get("incident_id")) else ""
                    d_narr = str(row["narrative"]).strip() if pd.notna(row.get("narrative")) else ""
                    if not d_narr or not d_id:
                        continue
                    if d_id in seen_ids:
                        continue
                    seen_ids.add(d_id)
                    d_cat = str(row.get("target_category", "unknown")).strip().lower()
                    d_sev = str(row.get("target_severity", "medium")).strip().lower()
                    all_records.append({
                        "incident_id": d_id,
                        "narrative": d_narr,
                        "target_category": d_cat if d_cat in ALLOWED_CATEGORIES else "unknown",
                        "target_severity": d_sev if d_sev in ALLOWED_SEVERITIES else "medium"
                    })
                logger.info(f"Loaded {len(all_records) - len(cleaned_baseline)} persisted dynamic incidents.")
            except Exception as e:
                logger.warning(f"Could not load dynamic incidents file: {e}")

        self._records = all_records
        self._is_loaded = len(self._records) > 0
        return self._records

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def records(self) -> List[Dict[str, Any]]:
        return list(self._records)

    @property
    def baseline_records(self) -> List[Dict[str, Any]]:
        return list(self._baseline_records)

    @property
    def validation_errors(self) -> List[str]:
        return list(self._validation_errors)

    def get_record(self, incident_id: str) -> Optional[Dict[str, Any]]:
        for rec in self._records:
            if rec["incident_id"].lower() == incident_id.lower():
                return dict(rec)
        return None

    def generate_next_id(self) -> str:
        """
        Generates the next sequential incident ID (e.g., S007, S008).
        """
        max_num = 0
        for rec in self._records:
            inc_id = rec.get("incident_id", "")
            match = re.match(r"^S(\d+)$", inc_id, re.IGNORECASE)
            if match:
                max_num = max(max_num, int(match.group(1)))
        if max_num > 0:
            return f"S{max_num + 1:03d}"
        return f"S{len(self._records) + 1:03d}"

    def add_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a single record to active memory and persists it to dynamic_incidents.csv
        so it survives server restarts.
        """
        self._records.append(record)
        self._persist_dynamic_record(record)
        return record

    def _persist_dynamic_record(self, record: Dict[str, Any]) -> None:
        """
        Appends the new record to dynamic_incidents.csv.
        """
        if not self.dynamic_path:
            return
        try:
            file_exists = self.dynamic_path.exists()
            with open(self.dynamic_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["incident_id", "narrative", "target_category", "target_severity"]
                )
                if not file_exists or self.dynamic_path.stat().st_size == 0:
                    writer.writeheader()
                writer.writerow({
                    "incident_id": record.get("incident_id", ""),
                    "narrative": record.get("narrative", ""),
                    "target_category": record.get("target_category", ""),
                    "target_severity": record.get("target_severity", "")
                })
        except Exception as e:
            logger.error(f"Failed to persist dynamic incident to {self.dynamic_path}: {e}")

    def reset_to_baseline(self) -> None:
        """
        Removes dynamic incidents storage file and restores only baseline records.
        """
        if self.dynamic_path and self.dynamic_path.exists():
            try:
                self.dynamic_path.unlink()
                logger.info(f"Removed dynamic incidents file {self.dynamic_path}")
            except Exception as e:
                logger.error(f"Failed to remove dynamic incidents file: {e}")
        self.load_data()


# Global singleton instance
data_service = DataService()
