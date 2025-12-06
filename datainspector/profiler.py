from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


@dataclass
class DataProfiler:
    """
    High-level dataset profiler that wraps common pandas/numpy operations.

    Design intent:
    - Provide a *single abstraction* that runs a standard set of profiling steps.
    - Return a structured dict so `ReportGenerator` can consume it consistently.
    - Generate plots (correlation heatmap, distributions) and return their file paths.

    This is more convenient than calling pandas/numpy directly because:
    - you don’t have to remember or repeat the individual calls for each new dataset;
    - the output format is stable, so downstream code (like reports) can rely on it.
    """

    data: pd.DataFrame
    output_dir: str = "reports"

    def summarize(self) -> Dict[str, Any]:
        """
        Compute and return a structured summary of the dataset.

        Returns a dict with:
        - shape
        - dtypes (column -> string)
        - missing_counts (column -> count)
        - missing_pct (column -> %)
        - duplicate_rows (int)
        - describe_numeric (nested dict of pandas .describe())
        - cardinality (for non-numeric columns)
        """
        df = self.data

        summary: Dict[str, Any] = {
            "shape": df.shape,
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_counts": df.isna().sum().to_dict(),
            "missing_pct": (df.isna().mean() * 100.0).round(2).to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
        }

        numeric = df.select_dtypes(include=[np.number])
        if not numeric.empty:
            summary["describe_numeric"] = numeric.describe().to_dict()
        else:
            summary["describe_numeric"] = {}

        cat_cols = df.select_dtypes(exclude=[np.number]).columns
        summary["cardinality"] = {c: int(df[c].nunique(dropna=True)) for c in cat_cols}

        return summary

    def correlate(self, method: str = "pearson") -> Dict[str, Any]:
        """
        Compute correlation matrix for numeric columns and save a heatmap.

        Returns:
            {
              "matrix": pandas.DataFrame or None,
              "figure_path": str or None,
              "note": optional string if there are no numeric columns
            }
        """
        os.makedirs(self.output_dir, exist_ok=True)

        num = self.data.select_dtypes(include=[np.number])
        if num.empty:
            return {"matrix": None, "figure_path": None, "note": "No numeric columns to correlate."}

        corr = num.corr(method=method)

        fig_path = os.path.join(self.output_dir, "correlation_heatmap.png")
        plt.figure(figsize=(6, 5))
        plt.imshow(corr, interpolation="nearest")
        plt.colorbar()
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
        plt.yticks(range(len(corr.columns)), corr.columns)
        plt.tight_layout()
        plt.savefig(fig_path, dpi=160)
        plt.close()

        return {"matrix": corr, "figure_path": fig_path}

    def visualize_distributions(self, max_cols: int = 12) -> Optional[str]:
        """
        Create a grid of histograms for up to `max_cols` numeric columns.

        Returns:
            Path to the saved PNG file, or None if there are no numeric columns.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        num = self.data.select_dtypes(include=[np.number]).iloc[:, :max_cols]
        if num.empty:
            return None

        n_cols = min(3, num.shape[1])
        n_rows = int(np.ceil(num.shape[1] / n_cols))

        plt.figure(figsize=(4 * n_cols, 3 * n_rows))
        for i, col in enumerate(num.columns, start=1):
            plt.subplot(n_rows, n_cols, i)
            plt.hist(num[col].dropna())
            plt.title(str(col))

        plt.tight_layout()
        fig_path = os.path.join(self.output_dir, "distributions.png")
        plt.savefig(fig_path, dpi=160)
        plt.close()

        return fig_path
