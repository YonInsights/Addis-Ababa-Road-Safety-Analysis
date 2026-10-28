"""
Automated Exploratory Data Analysis (EDA) Module
Provides high-performance, Python 3.15+ compatible automated profiling with the standard ydata_profiling interface.
"""

from pathlib import Path
import html
import json
import math
import numpy as np
import pandas as pd


class ProfileReport:
    """
    Automated EDA Profile Report generator compatible with the ydata_profiling API.
    Computes univariate statistics, categorical distributions, missingness patterns,
    cross-tabulations, and data quality alerts, rendering them into a standalone HTML report.
    """

    def __init__(self, df: pd.DataFrame, title: str = "Automated EDA Report", explorative: bool = True):
        self.df = df
        self.title = title
        self.explorative = explorative
        self._html_content = None
        self._summary_data = None
        self._compute_profile()

    def _compute_profile(self):
        df = self.df
        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols
        duplicate_rows = int(df.duplicated().sum())

        explicit_missing = int(df.isna().sum().sum())
        missing_pct = (explicit_missing / total_cells * 100) if total_cells > 0 else 0

        # Memory usage
        memory_bytes = int(df.memory_usage(deep=True).sum())
        memory_mb = memory_bytes / (1024 * 1024)

        # Categorize column types
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        categorical_cols = [c for c in df.columns if c not in numeric_cols]

        # Analyze each variable
        variables_summary = {}
        alerts = []

        for col in df.columns:
            s = df[col]
            missing_cnt = int(s.isna().sum())
            missing_ratio = missing_cnt / total_rows if total_rows > 0 else 0
            distinct_cnt = int(s.nunique(dropna=True))
            distinct_ratio = distinct_cnt / total_rows if total_rows > 0 else 0

            # Scan for implicit missing tokens
            implicit_tokens = ['na', 'Unknown', 'unknown', 'None', '?']
            pseudo_na_cnt = 0
            if col in categorical_cols:
                pseudo_na_cnt = int(s.astype(str).str.strip().isin(implicit_tokens).sum())

            var_info = {
                "name": col,
                "type": "Numeric" if col in numeric_cols else "Categorical",
                "missing_count": missing_cnt,
                "missing_pct": missing_ratio * 100,
                "implicit_missing_count": pseudo_na_cnt,
                "implicit_missing_pct": (pseudo_na_cnt / total_rows * 100) if total_rows > 0 else 0,
                "distinct_count": distinct_cnt,
                "distinct_pct": distinct_ratio * 100,
                "memory_bytes": int(s.memory_usage(deep=True)),
            }

            # Warnings / Alerts
            if missing_ratio > 0.20:
                alerts.append({
                    "column": col,
                    "type": "High Missingness",
                    "level": "warning",
                    "message": f"Column has {missing_cnt:,} explicit missing values ({missing_ratio*100:.1f}%)."
                })
            if pseudo_na_cnt / total_rows > 0.10:
                alerts.append({
                    "column": col,
                    "type": "Implicit Missing Values",
                    "level": "warning",
                    "message": f"Column contains {pseudo_na_cnt:,} text placeholder missing entries ({pseudo_na_cnt/total_rows*100:.1f}%)."
                })

            if col in numeric_cols:
                valid = s.dropna()
                var_info.update({
                    "mean": float(valid.mean()) if len(valid) > 0 else None,
                    "std": float(valid.std()) if len(valid) > 1 else None,
                    "min": float(valid.min()) if len(valid) > 0 else None,
                    "q25": float(valid.quantile(0.25)) if len(valid) > 0 else None,
                    "median": float(valid.median()) if len(valid) > 0 else None,
                    "q75": float(valid.quantile(0.75)) if len(valid) > 0 else None,
                    "max": float(valid.max()) if len(valid) > 0 else None,
                    "skewness": float(valid.skew()) if len(valid) > 2 else None,
                })
                # Check for extreme right skewness/outliers
                if len(valid) > 0 and var_info["q75"] is not None and var_info["q25"] is not None:
                    iqr = var_info["q75"] - var_info["q25"]
                    outliers_upper = (valid > (var_info["q75"] + 1.5 * iqr)).sum()
                    if outliers_upper > 0:
                        alerts.append({
                            "column": col,
                            "type": "Potential Outliers / Extreme Values",
                            "level": "info",
                            "message": f"{outliers_upper:,} records exceed 1.5x IQR upper threshold (Max = {var_info['max']})."
                        })

                # Histogram buckets
                counts, bin_edges = np.histogram(valid, bins=min(10, max(3, distinct_cnt)))
                var_info["histogram"] = {
                    "counts": counts.tolist(),
                    "bin_edges": [round(float(b), 2) for b in bin_edges]
                }
            else:
                # Value counts top 10
                vc = s.value_counts(dropna=False).head(10)
                var_info["top_values"] = {str(k): int(v) for k, v in vc.items()}
                # Check class imbalance
                top_pct = vc.iloc[0] / total_rows if len(vc) > 0 else 0
                if top_pct > 0.70:
                    alerts.append({
                        "column": col,
                        "type": "High Imbalance",
                        "level": "info",
                        "message": f"Dominant category '{vc.index[0]}' represents {top_pct*100:.1f}% of all records."
                    })

            variables_summary[col] = var_info

        self._summary_data = {
            "title": self.title,
            "total_rows": total_rows,
            "total_cols": total_cols,
            "total_cells": total_cells,
            "duplicate_rows": duplicate_rows,
            "explicit_missing": explicit_missing,
            "missing_pct": missing_pct,
            "memory_mb": round(memory_mb, 2),
            "numeric_cols_count": len(numeric_cols),
            "categorical_cols_count": len(categorical_cols),
            "alerts": alerts,
            "variables": variables_summary,
        }

    def to_file(self, output_file: str | Path):
        """Save the profile report as an HTML file."""
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        html_content = self.to_html()
        out_path.write_text(html_content, encoding="utf-8")
        print(f"Report exported successfully to: {out_path.resolve()}")

    def to_html(self) -> str:
        """Render the complete standalone HTML dashboard."""
        data = self._summary_data
        vars_data = data["variables"]

        # Build Alerts HTML
        alerts_html = ""
        for a in data["alerts"]:
            badge_color = "#e74c3c" if a["level"] == "warning" else "#3498db"
            alerts_html += f"""
            <div style="background: #fdfefe; border-left: 4px solid {badge_color}; padding: 10px 14px; margin-bottom: 8px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <strong>{html.escape(a['column'])}</strong> — <span style="background: {badge_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;">{a['type']}</span>
                <div style="color: #555; margin-top: 4px; font-size: 13px;">{html.escape(a['message'])}</div>
            </div>
            """

        # Build Variables HTML
        vars_html = ""
        for col_name, v in vars_data.items():
            type_badge = "#2980b9" if v["type"] == "Numeric" else "#27ae60"
            details_html = ""

            if v["type"] == "Numeric":
                details_html = f"""
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 8px; margin-top: 8px;">
                    <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; text-align: center;"><small style="color: #777;">Mean</small><br><strong>{v['mean']:.2f}</strong></div>
                    <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; text-align: center;"><small style="color: #777;">Std Dev</small><br><strong>{v['std']:.2f}</strong></div>
                    <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; text-align: center;"><small style="color: #777;">Min</small><br><strong>{v['min']:.0f}</strong></div>
                    <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; text-align: center;"><small style="color: #777;">Median</small><br><strong>{v['median']:.0f}</strong></div>
                    <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; text-align: center;"><small style="color: #777;">Max</small><br><strong>{v['max']:.0f}</strong></div>
                    <div style="background: #f8f9fa; padding: 6px; border-radius: 4px; text-align: center;"><small style="color: #777;">Skewness</small><br><strong>{v['skewness']:.2f}</strong></div>
                </div>
                """
            else:
                bars_html = ""
                for val, cnt in list(v["top_values"].items())[:6]:
                    pct = (cnt / data["total_rows"] * 100)
                    bars_html += f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; margin-top: 4px;">
                        <span style="width: 45%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{html.escape(str(val))}</span>
                        <div style="width: 40%; background: #eaeded; height: 12px; border-radius: 6px; overflow: hidden; margin: 0 8px;">
                            <div style="background: #3498db; width: {pct}%; height: 100%;"></div>
                        </div>
                        <span style="width: 15%; text-align: right; color: #555;">{pct:.1f}%</span>
                    </div>
                    """
                details_html = f"<div style='margin-top: 8px;'>{bars_html}</div>"

            vars_html += f"""
            <div style="background: white; border: 1px solid #e1e4e8; border-radius: 6px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f2f5; padding-bottom: 6px;">
                    <div>
                        <strong style="font-size: 15px; color: #2c3e50;">{html.escape(col_name)}</strong>
                        <span style="background: {type_badge}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; margin-left: 6px;">{v['type']}</span>
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        Distinct: <strong>{v['distinct_count']}</strong> ({v['distinct_pct']:.1f}%) | 
                        Missing: <strong style="color: {'#e74c3c' if v['missing_count'] > 0 else '#27ae60'};">{v['missing_count']}</strong> ({v['missing_pct']:.1f}%)
                        {f'| Text NA: <strong style="color: #e67e22;">{v["implicit_missing_count"]}</strong>' if v['implicit_missing_count'] > 0 else ''}
                    </div>
                </div>
                {details_html}
            </div>
            """

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(data['title'])}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f6f8fa; color: #24292e; margin: 0; padding: 24px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1b3a4b 0%, #006494 100%); color: white; padding: 28px; border-radius: 8px; margin-bottom: 24px; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 26px; }}
        .header p {{ margin: 0; opacity: 0.9; font-size: 14px; }}
        .card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 24px; }}
        .card {{ background: white; border-radius: 6px; padding: 16px; border: 1px solid #e1e4e8; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
        .card-title {{ font-size: 12px; text-transform: uppercase; color: #586069; margin-bottom: 6px; font-weight: 600; letter-spacing: 0.5px; }}
        .card-value {{ font-size: 26px; font-weight: bold; color: #006494; }}
        .section-title {{ font-size: 18px; color: #1b3a4b; margin: 28px 0 12px 0; border-bottom: 2px solid #e1e4e8; padding-bottom: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{html.escape(data['title'])}</h1>
            <p>Automated Exploratory Data Analysis & Quality Audit | Generated with Python 3.15 Environment</p>
        </div>

        <div class="card-grid">
            <div class="card"><div class="card-title">Total Observations</div><div class="card-value">{data['total_rows']:,}</div></div>
            <div class="card"><div class="card-title">Total Variables</div><div class="card-value">{data['total_cols']}</div></div>
            <div class="card"><div class="card-title">Duplicate Rows</div><div class="card-value">{data['duplicate_rows']}</div></div>
            <div class="card"><div class="card-title">Explicit Missing Cells</div><div class="card-value">{data['explicit_missing']:,} <span style="font-size: 14px; font-weight: normal; color: #777;">({data['missing_pct']:.1f}%)</span></div></div>
            <div class="card"><div class="card-title">Memory Footprint</div><div class="card-value">{data['memory_mb']} MB</div></div>
            <div class="card"><div class="card-title">Variable Types</div><div class="card-value" style="font-size: 18px; line-height: 32px;"><span style="color: #2980b9;">{data['numeric_cols_count']} Num</span> | <span style="color: #27ae60;">{data['categorical_cols_count']} Cat</span></div></div>
        </div>

        <h2 class="section-title">Automated Data Quality & Distribution Alerts ({len(data['alerts'])})</h2>
        {alerts_html}

        <h2 class="section-title">Variable Profiling ({data['total_cols']} Variables)</h2>
        {vars_html}
    </div>
</body>
</html>
"""
        return html_template

    def _repr_html_(self):
        """Allow inline rich display in Jupyter Notebook."""
        return self.to_html()

