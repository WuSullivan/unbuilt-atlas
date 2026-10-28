#!/usr/bin/env python3
"""Build the 80-project evidence ledger and deduplicated source register."""
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
with (ROOT / "data/nanyang_projects.csv").open(encoding="utf-8", newline="") as file:
    projects = list(csv.DictReader(file))
wayback_pairs = json.loads((ROOT / "data/wayback_pairs.json").read_text(encoding="utf-8"))

ledger = []
source_index = defaultdict(lambda: {"dates": set(), "roles": set(), "projects": set()})


def add_source(url, date, role, project_id):
    if not url:
        return
    record = source_index[url]
    if date:
        record["dates"].add(date)
    record["roles"].add(role)
    record["projects"].add(project_id)


for project in projects:
    pid = project["project_id"]
    role = project["cohort_role"]
    ledger.append({
        "project_id": pid,
        "cohort_role": role,
        "stage": "inclusion",
        "finding": "confirmed_named_project",
        "certainty": "primary_or_official_source",
        "source_url": project["source_sign"],
        "audit_note": "The project is explicitly named in the recorded signing or cohort source.",
    })
    add_source(project["source_sign"], project["sign_date"], "cohort inclusion", pid)

    status = project["followup_status"]
    located = status not in {"no_later_trace_located", "no_physical_milestone_located"}
    ledger.append({
        "project_id": pid,
        "cohort_role": role,
        "stage": "post_signing_followup",
        "finding": status,
        "certainty": f"evidence_grade_{project['evidence_grade']}",
        "source_url": project["source_followup"],
        "audit_note": project["followup_reason"],
    })
    add_source(project["source_followup"], project["followup_date"], "primary follow-up", pid)
    add_source(project["source_followup_secondary"], project["followup_date"], "secondary corroboration", pid)

    for stage, source_field, check_field in (
        ("environment", "source_environment", "environment_check"),
        ("local_registry", "source_registry", "registry_check"),
    ):
        source = project[source_field]
        finding = project[check_field] if project[check_field] else "not_systematically_verified"
        ledger.append({
            "project_id": pid,
            "cohort_role": role,
            "stage": stage,
            "finding": "source_captured" if source else finding,
            "certainty": "primary_source" if source else "not_a_negative_finding",
            "source_url": source,
            "audit_note": (
                f"A project-specific {stage} source is linked."
                if source
                else f"No systematic row-level {stage} extract was captured; blank is not a failure finding."
            ),
        })
        add_source(source, "", stage, pid)

    pair = wayback_pairs[pid]
    before = pair["before"]
    after = pair["after"]
    ledger.append({
        "project_id": pid,
        "cohort_role": role,
        "stage": "imagery",
        "finding": pair["comparison_type"],
        "certainty": f"distinct_center_tile_bytes_zoom_{pair['zoom']}",
        "source_url": "https://livingatlas.arcgis.com/wayback/",
        "audit_note": (
            f"Two non-identical center-tile files at the same indicator point and zoom {pair['zoom']} "
            f"(SHA-256 {before['tile_sha256'][:12]} != {after['tile_sha256'][:12]}). "
            f"Capture dates: {before['capture_date'] or 'not returned'} and {after['capture_date'] or 'not returned'}; "
            f"Wayback release dates: {before['release_date']} and {after['release_date']}. "
            "Coordinates are county/park/town indicators, not parcels; imagery does not determine project status."
        ),
    })

ledger_path = ROOT / "data/evidence_ledger.csv"
fields = ["project_id", "cohort_role", "stage", "finding", "certainty", "source_url", "audit_note"]
with ledger_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(ledger)

source_path = ROOT / "data/source_register.csv"
source_fields = ["source_id", "source_date", "source_url", "source_role", "projects_or_scope"]
with source_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=source_fields, lineterminator="\n")
    writer.writeheader()
    for index, (url, record) in enumerate(sorted(source_index.items()), 1):
        writer.writerow({
            "source_id": f"S{index:03d}",
            "source_date": ";".join(sorted(record["dates"])),
            "source_url": url,
            "source_role": "; ".join(sorted(record["roles"])),
            "projects_or_scope": ";".join(sorted(record["projects"])),
        })

print(ledger_path, len(ledger))
print(source_path, len(source_index))
