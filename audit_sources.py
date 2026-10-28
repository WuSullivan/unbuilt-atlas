#!/usr/bin/env python3
"""Check whether cited source URLs remain reachable without changing evidence codes."""
from __future__ import annotations

import csv
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/source_register.csv"
OUTPUT = ROOT / "outputs/source_health.csv"
TIMEOUT_SECONDS = 18
WORKERS = 10
USER_AGENT = "UnbuiltAtlasSourceAudit/1.0 (+public research link check)"


def request(url: str, method: str):
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*;q=0.8"}
    if method == "GET":
        headers["Range"] = "bytes=0-2047"
    req = Request(url, headers=headers, method=method)
    context = ssl.create_default_context()
    return urlopen(req, timeout=TIMEOUT_SECONDS, context=context)


def classify(status: int | str, error: str) -> str:
    if isinstance(status, int) and 200 <= status < 400:
        return "reachable"
    if status in {401, 403, 429}:
        return "restricted_or_rate_limited"
    if status in {404, 410}:
        return "not_found"
    if isinstance(status, int):
        return "http_error"
    if "timed out" in error.lower():
        return "timeout"
    return "connection_error"


def check(row: dict[str, str]) -> dict[str, str]:
    url = row["source_url"].strip()
    status: int | str = ""
    final_url = url
    error = ""
    for method in ("HEAD", "GET"):
        try:
            with request(url, method) as response:
                status = response.status
                final_url = response.geturl()
                error = ""
                break
        except HTTPError as exc:
            status = exc.code
            final_url = exc.geturl() or url
            error = f"HTTP {exc.code}"
            if method == "HEAD" and exc.code in {400, 403, 405, 406, 429, 501}:
                continue
            break
        except (URLError, TimeoutError, OSError) as exc:
            error = str(getattr(exc, "reason", exc))
            if method == "HEAD":
                continue
            break

    return {
        "source_id": row["source_id"],
        "url": url,
        "http_status": str(status),
        "final_url": final_url,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": classify(status, error),
        "error_detail": error,
    }


def main() -> None:
    with INPUT.open(encoding="utf-8", newline="") as handle:
        sources = list(csv.DictReader(handle))

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(check, row): row["source_id"] for row in sources}
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda row: int(row["source_id"][1:]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["source_id", "url", "http_status", "final_url", "checked_at", "note", "error_detail"]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    counts: dict[str, int] = {}
    for row in results:
        counts[row["note"]] = counts.get(row["note"], 0) + 1
    print(OUTPUT)
    print("checked:", len(results), counts)


if __name__ == "__main__":
    main()
