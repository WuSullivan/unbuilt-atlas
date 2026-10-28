#!/usr/bin/env python3
"""Assemble stable, user-facing dataset and publication archives."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
DATASET_DIR = OUTPUTS / "dataset"
SITE_DIR = OUTPUTS / "interactive-map"

DATA_FILES = [
    "events.csv",
    "nanyang_projects.csv",
    "followup_search_results.csv",
    "evidence_ledger.csv",
    "source_register.csv",
    "wayback_pairs.json",
    "README.md",
    "method.md",
    "decision_log.md",
    "field_dictionary.md",
]

PUBLIC_ROOT_FILES = [
    ".nojekyll",
    "CITATION.cff",
    "LICENSE",
    "README.md",
    "requirements.txt",
    "analysis.py",
    "audit_sources.py",
    "build_brief_pdf.py",
    "build_evidence_ledger.py",
    "build_expanded_atlas.py",
    "build_wayback_pairs.py",
    "build_publication.py",
    "build_site_data.py",
    "curate_followups.py",
    "index.html",
    "search_followups.py",
    "verify.sh",
]


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def add_file(archive: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo.from_file(path, arcname)
    info.date_time = (2026, 10, 29, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, path.read_bytes())


def main() -> None:
    reset_dir(DATASET_DIR)
    for name in DATA_FILES:
        source = ROOT / "data" / name
        shutil.copy2(source, DATASET_DIR / name)
    for name in ("analysis_summary.json", "model_results.csv", "project_status_counts.csv", "source_health.csv"):
        source = OUTPUTS / name
        if source.exists():
            shutil.copy2(source, DATASET_DIR / name)

    reset_dir(SITE_DIR)
    shutil.copy2(ROOT / "site/index.html", SITE_DIR / "index.html")
    shutil.copy2(ROOT / "site/atlas-data.js", SITE_DIR / "atlas-data.js")

    dataset_zip = OUTPUTS / "unbuilt-atlas-dataset.zip"
    with zipfile.ZipFile(dataset_zip, "w") as archive:
        for path in sorted(DATASET_DIR.rglob("*")):
            if path.is_file():
                add_file(archive, path, f"unbuilt-atlas-dataset/{path.relative_to(DATASET_DIR)}")

    publication_zip = OUTPUTS / "unbuilt-atlas-publication.zip"
    with zipfile.ZipFile(publication_zip, "w") as archive:
        for name in PUBLIC_ROOT_FILES:
            add_file(archive, ROOT / name, f"unbuilt-atlas/{name}")
        for path in sorted((ROOT / ".github").rglob("*")):
            if path.is_file():
                add_file(archive, path, f"unbuilt-atlas/{path.relative_to(ROOT)}")
        for folder in ("brief", "data", "site"):
            for path in sorted((ROOT / folder).rglob("*")):
                if path.is_file():
                    add_file(archive, path, f"unbuilt-atlas/{path.relative_to(ROOT)}")
        for name in (
            "analysis_summary.json",
            "application-story.md",
            "model_results.csv",
            "project_status_counts.csv",
            "source_health.csv",
            "unbuilt-atlas-research-brief.pdf",
        ):
            path = OUTPUTS / name
            if path.exists():
                add_file(archive, path, f"unbuilt-atlas/outputs/{name}")

    print(DATASET_DIR)
    print(SITE_DIR)
    print(dataset_zip)
    print(publication_zip)


if __name__ == "__main__":
    main()
