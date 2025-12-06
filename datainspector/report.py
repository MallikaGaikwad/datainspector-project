from __future__ import annotations

import datetime
import html
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ReportGenerator:
    """
    Compile profiling and validation results into a simple HTML report.

    The design assumes:
    - `profile` comes from DataProfiler.summarize()
    - `validation` comes from DataValidator.validate()
    - correlation/distribution figure paths come from DataProfiler methods

    This separation keeps the report layer focused on presentation, not computation.
    """

    output_dir: str = "reports"
    title: str = "datainspector Report"

    def _ensure_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    def _html_table(self, mapping: Dict[str, Any]) -> str:
        rows = []
        for key, value in mapping.items():
            rows.append(
                "<tr>"
                f"<th style='text-align:left;padding:4px 8px'>{html.escape(str(key))}</th>"
                f"<td style='padding:4px 8px'><pre style='margin:0'>{html.escape(str(value))}</pre></td>"
                "</tr>"
            )
        return "<table border='1' cellspacing='0' cellpadding='0'>" + "".join(rows) + "</table>"

    def compile_report(
        self,
        profile: Dict[str, Any],
        validation: Dict[str, Any],
        corr_fig: Optional[str],
        dist_fig: Optional[str],
    ) -> str:
        """
        Build an HTML string and save it to disk.

        Returns:
            Path to the saved HTML file.
        """
        self._ensure_dir()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        parts = [
            f"<h1>{html.escape(self.title)}</h1>",
            f"<p><em>Generated: {now}</em></p>",
            "<h2>Dataset Overview</h2>",
            self._html_table({
                "Shape": profile.get("shape"),
                "Duplicate rows": profile.get("duplicate_rows"),
            }),
            "<h2>Missingness (%)</h2>",
            self._html_table(profile.get("missing_pct", {})),
            "<h2>Dtypes</h2>",
            self._html_table(profile.get("dtypes", {})),
            "<h2>Validation Summary</h2>",
            f"<p><strong>Overall:</strong> {'PASS' if validation.get('passed') else 'FAIL'}</p>",
        ]

        if validation.get("errors"):
            parts.append("<h3>Global Errors</h3><ul>")
            for err in validation["errors"]:
                parts.append(f"<li>{html.escape(err)}</li>")
            parts.append("</ul>")

        if "columns" in validation:
            parts.append("<h3>Per-Column Issues</h3><ul>")
            for col, res in validation["columns"].items():
                if res.get("issues"):
                    parts.append(
                        f"<li><strong>{html.escape(col)}</strong>: "
                        + ", ".join(html.escape(i) for i in res["issues"])
                        + "</li>"
                    )
            parts.append("</ul>")

        if corr_fig:
            parts.append("<h2>Correlation Heatmap</h2>")
            parts.append(
                f"<img src='{html.escape(corr_fig)}' alt='Correlation Heatmap' width='600'/>"
            )

        if dist_fig:
            parts.append("<h2>Distributions</h2>")
            parts.append(
                f"<img src='{html.escape(dist_fig)}' alt='Distributions' width='600'/>"
            )

        html_str = "\n".join(parts)
        out_path = os.path.join(self.output_dir, "datainspector_report.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_str)

        return out_path

    def export(self, html_path: str, as_markdown: bool = False) -> str:
        """
        Stub for future extension. Currently just returns the HTML path.

        You could optionally add HTML-to-Markdown conversion here if needed.
        """
        return html_path
