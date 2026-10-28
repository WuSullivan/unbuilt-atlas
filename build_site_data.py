#!/usr/bin/env python3
"""Build the static site's data payload from canonical project files."""
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

with (ROOT / "data/nanyang_projects.csv").open(encoding="utf-8", newline="") as file:
    projects = list(csv.DictReader(file))
with (ROOT / "data/events.csv").open(encoding="utf-8", newline="") as file:
    events = list(csv.DictReader(file))
summary = json.loads((ROOT / "outputs/analysis_summary.json").read_text(encoding="utf-8"))
wayback_pairs = json.loads((ROOT / "data/wayback_pairs.json").read_text(encoding="utf-8"))

payload = {
    "projects": projects,
    "events": events,
    "summary": summary,
    "wayback_pairs": wayback_pairs,
    "imagery": {
        "provider": "Esri World Imagery Wayback",
        "cutoff_date": "2025-12-31",
        "comparison_method": "Local Wayback tile history at each displayed coordinate and zoom, deduplicated by SHA-256 of tile bytes.",
    },
}

target = ROOT / "site/atlas-data.js"
target.write_text(
    "window.UNBUILT_ATLAS = "
    + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)
print(target)
