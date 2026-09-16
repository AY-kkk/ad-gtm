#!/usr/bin/env python3
"""Calculate comparable video-ad experiment metrics from a JSON export."""

import argparse
import json
from pathlib import Path


REQUIRED = {
    "campaign_id", "asset_id", "platform", "objective", "audience",
    "spend", "impressions", "clicks", "conversions", "revenue",
}


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def metrics(row):
    spend = float(row.get("spend", 0))
    impressions = int(row.get("impressions", 0))
    clicks = int(row.get("clicks", 0))
    conversions = int(row.get("conversions", 0))
    revenue = float(row.get("revenue", 0))
    production = float(row.get("production_cost", 0))
    accepted = int(row.get("accepted_outputs", 0))
    return {
        "ctr": ratio(clicks, impressions),
        "cvr_on_click": ratio(conversions, clicks),
        "cpc": ratio(spend, clicks),
        "cpa": ratio(spend, conversions),
        "roas": ratio(revenue, spend),
        "accepted_output_cost": ratio(production, accepted),
    }


def validate_row(row, index):
    missing = sorted(REQUIRED - set(row))
    if missing:
        raise ValueError(f"row {index} missing fields: {', '.join(missing)}")
    for field in ["spend", "impressions", "clicks", "conversions", "revenue"]:
        if float(row[field]) < 0:
            raise ValueError(f"row {index} has negative {field}")
    if int(row["clicks"]) > int(row["impressions"]):
        raise ValueError(f"row {index} clicks exceed impressions")
    if int(row["conversions"]) > int(row["clicks"]):
        raise ValueError(f"row {index} conversions exceed clicks")


def comparable(a, b):
    fields = ["platform", "objective", "audience", "attribution_window"]
    differences = [f for f in fields if a.get(f) != b.get(f)]
    return (not differences, differences)


def load_rows(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("campaigns", data) if isinstance(data, dict) else data
    if not isinstance(rows, list) or not rows:
        raise ValueError("input must contain a non-empty campaigns list")
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} is not an object")
        validate_row(row, index)
    return rows


def report(rows):
    lines = ["# Video Ad Benchmark Report", "", "Metrics are calculated from supplied counts. Null means the denominator is zero.", ""]
    lines.append("| Asset | Data status | Platform | Impressions | Clicks | Conversions | CTR | CVR (click) | CPA | ROAS | Accepted-output cost |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in rows:
        m = metrics(row)
        def fmt(value):
            if value is None:
                return "null"
            return f"{value:.4f}" if value < 1 else f"{value:.2f}"
        lines.append(
            f"| {row['asset_id']} | {row.get('data_status', 'unverified')} | {row['platform']} | "
            f"{int(row['impressions'])} | {int(row['clicks'])} | {int(row['conversions'])} | "
            f"{fmt(m['ctr'])} | {fmt(m['cvr_on_click'])} | {fmt(m['cpa'])} | {fmt(m['roas'])} | {fmt(m['accepted_output_cost'])} |"
        )
    lines += ["", "## Comparability", ""]
    if len(rows) > 1:
        same, differences = comparable(rows[0], rows[1])
        lines.append(f"First two rows directly comparable: **{'yes' if same else 'no'}**.")
        if differences:
            lines.append("Different fields: " + ", ".join(differences) + ".")
    else:
        lines.append("At least two comparable variants are required for a comparison.")
    lines += ["", "## Evidence boundary", "", "This report does not establish causality, incrementality, or a winning creative without a pre-specified comparable experiment and sufficient sample.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args(argv)
    rows = load_rows(args.input)
    if args.format == "json":
        result = {"rows": [{**row, "metrics": metrics(row)} for row in rows]}
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    else:
        text = report(rows)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
