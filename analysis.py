#!/usr/bin/env python3
"""Reproduce the event transparency, project outcomes, and signal model."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportion_confint


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

events = pd.read_csv(ROOT / "data/events.csv")
projects = pd.read_csv(ROOT / "data/nanyang_projects.csv")

# Event-level disclosure: count each non-overlapping primary article once.
counted_events = events[events["counting_role"] == "primary_event"].copy()
announced_slots = int(counted_events["announced_project_slots"].sum())
named_in_same_article = int(counted_events["named_physical_projects_in_article"].sum())
named_rate = named_in_same_article / announced_slots

# Project-level outcomes.
strong_statuses = {"built", "physical_progress"}
status_order = [
    "built",
    "physical_progress",
    "administrative_only",
    "later_mention_only",
    "no_later_trace_located",
    "no_physical_milestone_located",
]
status_counts = projects["followup_status"].value_counts().reindex(status_order, fill_value=0)
strong_count = int(projects["followup_status"].isin(strong_statuses).sum())
strong_rate = strong_count / len(projects)
strong_ci = proportion_confint(strong_count, len(projects), alpha=0.05, method="wilson")

deep = projects[projects["cohort_role"] == "xichuan_deep_audit"].copy()
deep_strong = int(deep["followup_status"].isin(strong_statuses).sum())

# The signal model is restricted to the 66-project broad cohort because its
# follow-up protocol is uniform. Company recognition and event size are the two
# pre-specified surface signals. Amount is not modeled: only 11/66 rows disclose
# a comparable project-level figure.
broad = projects[projects["cohort_role"] == "nanyang_named_project"].copy()
broad["strong_physical_milestone"] = broad["followup_status"].isin(strong_statuses).astype(int)
broad["recognizable_company"] = broad["company_signal"].isin(
    ["listed_company", "central_state_company", "national_company", "national_brand"]
).astype(int)
broad["log_event_slots"] = np.log1p(broad["event_announced_project_slots"].astype(float))
broad["log_event_slots_z"] = (
    broad["log_event_slots"] - broad["log_event_slots"].mean()
) / broad["log_event_slots"].std(ddof=0)

X = sm.add_constant(broad[["recognizable_company", "log_event_slots_z"]])
model = sm.GLM(
    broad["strong_physical_milestone"], X, family=sm.families.Binomial()
).fit()
model_ci = model.conf_int()

model_rows = []
labels = {
    "recognizable_company": "Recognizable company signal",
    "log_event_slots_z": "Event size (per 1 SD in log slots)",
}
for term in ("recognizable_company", "log_event_slots_z"):
    model_rows.append({
        "term": term,
        "label": labels[term],
        "odds_ratio": float(np.exp(model.params[term])),
        "ci95_low": float(np.exp(model_ci.loc[term, 0])),
        "ci95_high": float(np.exp(model_ci.loc[term, 1])),
        "p_value": float(model.pvalues[term]),
    })

known_yes_n = int((broad["recognizable_company"] == 1).sum())
known_no_n = int((broad["recognizable_company"] == 0).sum())
known_yes_rate = float(
    broad.loc[broad["recognizable_company"] == 1, "strong_physical_milestone"].mean()
)
known_no_rate = float(
    broad.loc[broad["recognizable_company"] == 0, "strong_physical_milestone"].mean()
)

summary = {
    "scope": {
        "region": "Nanyang, Henan, with a Xichuan deep-audit cohort",
        "signing_window": "2019-01-01 to 2022-12-31",
        "followup_cutoff": "2025-12-31",
        "event_articles": int(len(events)),
        "nonoverlapping_primary_events": int(len(counted_events)),
        "projects_total": int(len(projects)),
        "broad_named_projects": int(len(broad)),
        "xichuan_deep_audit_projects": int(len(deep)),
    },
    "event_transparency": {
        "announced_project_slots": announced_slots,
        "named_projects_in_same_article": named_in_same_article,
        "same_article_naming_rate": named_rate,
        "definition": "article-level project slots, not deduplicated physical projects",
    },
    "outcomes": {
        "status_counts": {k: int(v) for k, v in status_counts.items()},
        "strong_physical_milestone_count": strong_count,
        "strong_physical_milestone_rate": strong_rate,
        "strong_physical_milestone_ci95": [float(strong_ci[0]), float(strong_ci[1])],
        "no_project_specific_milestone_count": int(
            status_counts["no_later_trace_located"]
            + status_counts["no_physical_milestone_located"]
        ),
        "xichuan_strong_count": deep_strong,
        "xichuan_strong_rate": deep_strong / len(deep),
    },
    "surface_signals": {
        "recognizable_company_n": known_yes_n,
        "recognizable_company_strong_rate": known_yes_rate,
        "other_company_n": known_no_n,
        "other_company_strong_rate": known_no_rate,
        "project_amount_available_n": int(
            broad["announced_investment_cny_100m"].notna().sum()
        ),
        "project_amount_total_n": int(len(broad)),
        "model_n": int(len(broad)),
        "model_positive_outcomes": int(broad["strong_physical_milestone"].sum()),
        "model": model_rows,
    },
}

(OUT / "analysis_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
pd.DataFrame(model_rows).to_csv(OUT / "model_results.csv", index=False)
status_counts.rename_axis("followup_status").rename("count").to_csv(
    OUT / "project_status_counts.csv"
)

print("Unbuilt Atlas | expanded analysis")
print(f"Event articles: {len(events)}; non-overlapping primary events: {len(counted_events)}")
print(
    f"Same-article naming: {named_in_same_article}/{announced_slots} "
    f"({100 * named_rate:.1f}%)"
)
print(f"Project cohort: {len(projects)}")
print("Status counts:", {k: int(v) for k, v in status_counts.items()})
print(
    f"Strong physical milestone: {strong_count}/{len(projects)} "
    f"({100 * strong_rate:.1f}%; Wilson 95% CI "
    f"{100 * strong_ci[0]:.1f}-{100 * strong_ci[1]:.1f}%)"
)
print(
    "No project-specific milestone located: "
    f"{summary['outcomes']['no_project_specific_milestone_count']}/{len(projects)} "
    f"({100 * summary['outcomes']['no_project_specific_milestone_count'] / len(projects):.1f}%)"
)
print(
    f"Recognizable company: {100 * known_yes_rate:.1f}% ({known_yes_n} projects); "
    f"other/undisclosed: {100 * known_no_rate:.1f}% ({known_no_n} projects)"
)
for row in model_rows:
    print(
        f"{row['label']}: OR {row['odds_ratio']:.2f}, "
        f"95% CI {row['ci95_low']:.2f}-{row['ci95_high']:.2f}, "
        f"p={row['p_value']:.3f}"
    )
print(
    "Amount model not fit:",
    summary["surface_signals"]["project_amount_available_n"],
    "/",
    len(broad),
    "comparable project-level amounts",
)
