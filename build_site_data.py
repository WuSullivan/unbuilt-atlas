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

payload = {
    "projects": projects,
    "events": events,
    "summary": summary,
    "imagery": {
        "before": {
            "label": "Esri Wayback release 2022-06-08",
            "url": "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/44710/{z}/{y}/{x}",
        },
        "after": {
            "label": "Esri Wayback release 2025-12-18",
            "url": "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/13192/{z}/{y}/{x}",
        },
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
