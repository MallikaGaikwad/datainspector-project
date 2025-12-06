from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, Any

import numpy as np
import pandas as pd

# Map human-friendly type names to Python / NumPy types
TYPE_MAP = {
    "int": (np.integer, int),
    "float": (np.floating, float, int), 
    "string": (object, str),
    "bool": (np.bool_, bool),
    "date": (np.datetime64,),
}


@dataclass
class DataValidator:
    """
    Validate a pandas DataFrame against a JSON schema.

    Schema format (simplified):
    {
      "columns": {
        "age": {
          "type": "int",
          "required": true,
          "min": 18,
          "max": 100
        },
        "plan": {
          "type": "string",
          "allowed": ["Basic", "Standard", "Premium"]
        }
      }
    }
    """

    schema: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load_schema(cls, schema_path: str) -> "DataValidator":
        """Load schema from a JSON file and return a DataValidator instance."""
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return cls(schema=schema)

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run all checks specified in the schema.

        Returns a dict with keys:
        - passed: bool
        - errors: list of global errors (e.g., missing required columns)
        - warnings: list (reserved for future use)
        - columns: {col_name: {"passes": bool, "issues": [str, ...]}, ...}
        """
        results: Dict[str, Any] = {"columns": {}, "errors": [], "warnings": []}

        # Check required columns
        required_cols = [
            col for col, cfg in self.schema.get("columns", {}).items()
            if cfg.get("required", False)
        ]
        for col in required_cols:
            if col not in df.columns:
                results["errors"].append(f"Missing required column '{col}'")

        # Per-column checks
        for col, cfg in self.schema.get("columns", {}).items():
            if col not in df.columns:
                continue

            series = df[col]
            col_res = {"passes": True, "issues": []}

            # Type check
            expected_type = cfg.get("type")
            if expected_type:
                if expected_type == "date":
                    if not pd.api.types.is_datetime64_any_dtype(series):
                        try:
                            pd.to_datetime(series, errors="raise")
                        except Exception:
                            col_res["passes"] = False
                            col_res["issues"].append("Type mismatch: not parseable as date")
                else:
                    py_types = TYPE_MAP.get(expected_type, ())
                    invalid_mask = series.dropna().map(
                        lambda x: isinstance(x, tuple(py_types))
                    ).eq(False)
                    if invalid_mask.any():
                        n_inv = int(invalid_mask.sum())
                        col_res["passes"] = False
                        col_res["issues"].append(
                            f"Type mismatch: {n_inv} value(s) not {expected_type}"
                        )

            # Range checks
            if "min" in cfg:
                below = series[series < cfg["min"]].shape[0]
                if below > 0:
                    col_res["passes"] = False
                    col_res["issues"].append(f"{below} value(s) below min {cfg['min']}")

            if "max" in cfg:
                above = series[series > cfg["max"]].shape[0]
                if above > 0:
                    col_res["passes"] = False
                    col_res["issues"].append(f"{above} value(s) above max {cfg['max']}")

            # Allowed set
            if "allowed" in cfg:
                invalid = ~series.isin(cfg["allowed"])
                invalid = invalid & series.notna()
                if invalid.any():
                    col_res["passes"] = False
                    col_res["issues"].append(
                        f"{int(invalid.sum())} value(s) not in allowed set"
                    )

            # Regex pattern
            if "regex" in cfg:
                pattern = re.compile(cfg["regex"])
                invalid = series.dropna().map(
                    lambda x: bool(pattern.fullmatch(str(x)))
                ).eq(False)
                if invalid.any():
                    col_res["passes"] = False
                    col_res["issues"].append(
                        f"{int(invalid.sum())} value(s) fail regex '{cfg['regex']}'"
                    )

            results["columns"][col] = col_res

        results["passed"] = (
            len(results["errors"]) == 0
            and all(c["passes"] for c in results["columns"].values())
        )
        return results

    def generate_summary(self, results: Dict[str, Any]) -> str:
        """Return a short human-readable summary for the report."""
        if results.get("passed"):
            return "All validation checks passed."

        parts = []
        if results.get("errors"):
            parts.append(f"Errors: {len(results['errors'])}")
        failed_cols = sum(
            1 for c in results.get("columns", {}).values() if not c.get("passes", False)
        )
        parts.append(f"Columns with issues: {failed_cols}")
        return "; ".join(parts)
