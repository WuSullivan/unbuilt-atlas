#!/usr/bin/env python3
"""Search public web results for post-signing project milestones.

The output is a candidate ledger for review, not an automatic truth label.
"""
import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
SEARCH_URL = "https://so.toutiao.com/search"
GENERIC = "项目建设生产线生产基地产业园年产南阳市南阳卧龙区西峡县内乡县桐柏县南召县宛城区高新区方城县" 
BUILT = ("投产", "试产", "达产", "建成投用", "建成运营", "竣工", "正式运营", "投入使用")
PHYSICAL = ("开工", "奠基", "施工", "封顶", "厂房", "建设中", "加快建设", "设备进场", "主体完工")
ADMIN = ("环评", "批复", "许可", "备案", "公示", "用地", "规划审批")


def clean(text):
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", text or "")


def distinctive(text):
    value = clean(text)
    for char in GENERIC:
        value = value.replace(char, "")
    return value or clean(text)


def direct_url(href):
    if not href:
        return ""
    query = parse_qs(urlparse(href).query)
    nested = query.get("url", [href])[0]
    decoded = unquote(nested)
    match = re.search(r"h5_url=([^&]+)", decoded)
    if match:
        decoded = unquote(match.group(1))
    for _ in range(2):
        if "%" in decoded:
            decoded = unquote(decoded)
    return decoded if decoded.startswith("http") else ""


def relevance(name, card_text):
    target = distinctive(name)
    observed = distinctive(card_text)
    if target and target in observed:
        return 1.0
    if len(target) < 3:
        return 0.0
    bigrams = {target[i:i + 2] for i in range(len(target) - 1)}
    recall = sum(token in observed for token in bigrams) / max(1, len(bigrams))
    return max(recall, SequenceMatcher(None, target, observed[: max(40, len(target) * 5)]).ratio())


def result_cards(html, project_name):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for card in soup.select(".result-content .l-card"):
        title_link = card.select_one("a.l-card-title")
        if not title_link:
            continue
        text = re.sub(r"\s+", " ", card.get_text(" ", strip=True))
        title = re.sub(r"\s+", " ", title_link.get_text(" ", strip=True))
        score = relevance(project_name, title + " " + text)
        results.append({
            "result_title": title,
            "result_text": text[:700],
            "result_url": direct_url(title_link.get("href")),
            "relevance_score": round(score, 3),
        })
    results.sort(key=lambda row: row["relevance_score"], reverse=True)
    return results[:5]


def search(row):
    key = row["company_name"] or distinctive(row["project_name"])[:18]
    queries = [
        f"{row['county']} {row['project_name']} 开工 投产",
        f"{row['county']} {key} 项目 进展 竣工",
    ]
    combined = []
    seen = set()
    for query in queries:
        response = requests.get(
            SEARCH_URL, params={"keyword": query},
            headers={"User-Agent": "Mozilla/5.0"}, timeout=35,
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        for card in result_cards(response.text, row["project_name"]):
            identity = (card["result_title"], card["result_url"])
            if identity not in seen:
                combined.append(card | {"query_variant": query})
                seen.add(identity)
    combined.sort(key=lambda card: card["relevance_score"], reverse=True)
    return row, combined[:8]


with (ROOT / "data/nanyang_projects.csv").open(encoding="utf-8", newline="") as file:
    projects = [row for row in csv.DictReader(file) if row["cohort_role"] == "nanyang_named_project"]

ledger = []
with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(search, row): row for row in projects}
    for index, future in enumerate(as_completed(futures), 1):
        project = futures[future]
        try:
            row, cards = future.result()
        except Exception as exc:
            ledger.append({
                "project_id": project["project_id"], "query": "", "rank": "",
                "result_title": "", "result_text": "", "result_url": "",
                "relevance_score": "", "milestone_guess": "search_error",
                "review_note": str(exc),
            })
            continue
        if not cards:
            cards = [{"result_title": "", "result_text": "", "result_url": "", "relevance_score": 0, "query_variant": ""}]
        for rank, card in enumerate(cards, 1):
            text = card["result_title"] + " " + card["result_text"]
            if card["relevance_score"] < 0.35:
                guess = "not_relevant"
            elif any(word in text for word in BUILT):
                guess = "built_candidate"
            elif any(word in text for word in PHYSICAL):
                guess = "physical_progress_candidate"
            elif any(word in text for word in ADMIN):
                guess = "administrative_candidate"
            else:
                guess = "later_trace_candidate"
            ledger.append({
                "project_id": row["project_id"], "query": card.pop("query_variant"), "rank": rank,
                **card, "milestone_guess": guess, "review_note": "",
            })
        print(f"{index:02d}/{len(projects)} {row['project_id']} {row['project_name']} -> {cards[0]['relevance_score']}", flush=True)
        time.sleep(0.05)

fields = ["project_id", "query", "rank", "result_title", "result_text", "result_url", "relevance_score", "milestone_guess", "review_note"]
with (ROOT / "data/followup_search_results.csv").open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(ledger, key=lambda row: (row["project_id"], str(row["rank"]))))
print(ROOT / "data/followup_search_results.csv", len(ledger))
