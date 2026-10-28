#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"

BUNDLED_PYTHON=/Users/sullivan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
if [ -x "$BUNDLED_PYTHON" ]; then
  PYTHON_BIN=$BUNDLED_PYTHON
else
  PYTHON_BIN=python3
fi

echo "[1/4] Rebuilding datasets and derived artifacts"
"$PYTHON_BIN" build_expanded_atlas.py
"$PYTHON_BIN" curate_followups.py
"$PYTHON_BIN" analysis.py
"$PYTHON_BIN" build_evidence_ledger.py
"$PYTHON_BIN" build_site_data.py
"$PYTHON_BIN" build_brief_pdf.py

echo "[2/4] Checking research invariants"
"$PYTHON_BIN" - <<'PY'
import csv
import json
from collections import Counter
from pathlib import Path

root = Path('.')

def rows(path):
    with (root / path).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))

events = rows('data/events.csv')
projects = rows('data/nanyang_projects.csv')
project_by_id = {row['project_id']: row for row in projects}
search = rows('data/followup_search_results.csv')
ledger = rows('data/evidence_ledger.csv')
sources = rows('data/source_register.csv')
wayback_pairs = json.loads((root / 'data/wayback_pairs.json').read_text(encoding='utf-8'))
summary = json.loads((root / 'outputs/analysis_summary.json').read_text(encoding='utf-8'))

assert len(events) == 24, len(events)
primary = [row for row in events if row['counting_role'] == 'primary_event']
assert len(primary) == 21, len(primary)
assert sum(int(row['announced_project_slots']) for row in primary) == 426
assert sum(int(row['named_physical_projects_in_article']) for row in primary) == 62

assert len(projects) == 80, len(projects)
assert len({row['project_id'] for row in projects}) == 80
assert sum(row['cohort_role'] == 'nanyang_named_project' for row in projects) == 66
assert sum(row['cohort_role'] == 'xichuan_deep_audit' for row in projects) == 14

expected = {
    'built': 5,
    'physical_progress': 9,
    'administrative_only': 3,
    'later_mention_only': 5,
    'no_later_trace_located': 47,
    'no_physical_milestone_located': 11,
}
counts = Counter(row['followup_status'] for row in projects)
assert dict(counts) == expected, counts
assert sum(counts[key] for key in ('built', 'physical_progress')) == 14
assert counts['no_later_trace_located'] + counts['no_physical_milestone_located'] == 58

assert len(search) == 497, len(search)
assert len(ledger) == 400, len(ledger)
assert Counter(row['stage'] for row in ledger) == {
    'inclusion': 80,
    'post_signing_followup': 80,
    'environment': 80,
    'local_registry': 80,
    'imagery': 80,
}
assert len(sources) >= 45, len(sources)
assert len({row['source_url'] for row in sources}) == len(sources)
assert len(wayback_pairs) == 80, len(wayback_pairs)
pair_types = Counter(pair['comparison_type'] for pair in wayback_pairs.values())
assert pair_types == Counter({
    'acquisition_dates_bracket_signing': 62,
    'latest_distinct_image_no_verified_post_sign_capture': 16,
    'post_sign_capture_before_capture_unknown': 2,
}), pair_types
for project_id, pair in wayback_pairs.items():
    assert pair['locally_distinct'] is True, project_id
    assert pair['before']['tile_sha256'] != pair['after']['tile_sha256'], project_id
    assert pair['before']['tile_url'] != pair['after']['tile_url'], project_id
    if pair['before']['capture_date']:
        assert pair['before']['capture_date'] != pair['after']['capture_date'], project_id
    sign_date = project_by_id[project_id]['sign_date']
    if pair['comparison_type'] == 'acquisition_dates_bracket_signing':
        assert pair['before']['capture_date'] <= sign_date < pair['after']['capture_date'], project_id
    elif pair['comparison_type'] == 'post_sign_capture_before_capture_unknown':
        assert pair['after']['capture_date'] > sign_date, project_id
        assert not pair['before']['capture_date'], project_id
    else:
        assert pair['comparison_type'] == 'latest_distinct_image_no_verified_post_sign_capture', project_id
        assert not pair['after']['capture_date'] or pair['after']['capture_date'] <= sign_date, project_id

assert summary['scope']['nonoverlapping_primary_events'] == 21
assert summary['event_transparency']['announced_project_slots'] == 426
assert summary['event_transparency']['named_projects_in_same_article'] == 62
assert summary['outcomes']['status_counts'] == expected
assert summary['outcomes']['strong_physical_milestone_count'] == 14
assert summary['outcomes']['no_project_specific_milestone_count'] == 58
assert summary['surface_signals']['model_n'] == 66
assert len(summary['surface_signals']['model']) == 2

print('events:', len(events), 'primary:', len(primary), 'slots:', 426, 'named:', 62)
print('projects:', len(projects), 'broad:', 66, 'deep:', 14)
print('status counts:', dict(counts))
print('search candidates:', len(search), 'ledger rows:', len(ledger), 'sources:', len(sources))
print('locally distinct imagery pairs:', len(wayback_pairs))
PY

echo "[3/4] Checking website and PDF"
test -s site/index.html
test -s site/atlas-data.js
test -s outputs/unbuilt-atlas-research-brief.pdf
grep -q 'UNBUILT_ATLAS' site/atlas-data.js
grep -q 'markerClusterGroup' site/index.html
grep -q 'satBefore' site/index.html
grep -q 'oddsPlot' site/index.html
"$PYTHON_BIN" - <<'PY'
import pymupdf

document = pymupdf.open('outputs/unbuilt-atlas-research-brief.pdf')
assert document.page_count == 3, document.page_count
for index, page in enumerate(document, 1):
    text = page.get_text().strip()
    assert len(text) > 250, (index, len(text))
print('brief pages:', document.page_count)
PY

echo "[4/4] Verification complete"
echo "PASS: the 80-project atlas, model, evidence ledger, map data, and brief reproduce."
