#!/usr/bin/env python3
"""Select locally distinct Esri Wayback releases for every project point.

The script follows Esri's tilemap change chain at the exact display zoom,
compares tile bytes to remove duplicate imagery, and records acquisition
metadata for a release before signing and the latest changed release before
the study cutoff. The result is static so the public site does not need to
run a slow historical-imagery search in each visitor's browser.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
PROJECTS_FILE = ROOT / "data/nanyang_projects.csv"
OUTPUT_FILE = ROOT / "data/wayback_pairs.json"
CACHE_FILE = ROOT / "work/wayback_point_cache.json"
CONFIG_URL = "https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json"
TILEMAP_ROOT = "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tilemap"
CUTOFF = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
USER_AGENT = "UnbuiltAtlasWaybackBuilder/1.0"
TIMEOUT = 45
WORKERS = 6


def fetch(url: str, *, binary: bool = False, attempts: int = 3, timeout: int = TIMEOUT):
    last_error = None
    for attempt in range(attempts):
        request = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read()
            return body if binary else json.loads(body)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise last_error


def long2tile(longitude: float, zoom: int) -> int:
    return int((longitude + 180.0) / 360.0 * (2**zoom))


def lat2tile(latitude: float, zoom: int) -> int:
    latitude_rad = math.radians(latitude)
    return int(
        (1.0 - math.asinh(math.tan(latitude_rad)) / math.pi)
        / 2.0
        * (2**zoom)
    )


def release_date(item: dict) -> datetime:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", item["itemTitle"])
    if not match:
        raise ValueError(f"Missing release date: {item['itemTitle']}")
    return datetime.fromisoformat(match.group(1)).replace(tzinfo=timezone.utc)


def tile_url(item: dict, zoom: int, row: int, column: int) -> str:
    return (
        item["itemURL"]
        .replace("{level}", str(zoom))
        .replace("{row}", str(row))
        .replace("{col}", str(column))
    )


def leaflet_url(item: dict) -> str:
    return (
        item["itemURL"]
        .replace("{level}", "{z}")
        .replace("{row}", "{y}")
        .replace("{col}", "{x}")
    )


def metadata(item: dict, longitude: float, latitude: float, zoom: int) -> dict:
    layer_id = min(13, 23 - zoom)
    params = urlencode(
        {
            "f": "json",
            "where": "1=1",
            "outFields": "SRC_DATE2,NICE_DESC,SRC_DESC,SAMP_RES,SRC_ACC",
            "geometry": json.dumps(
                {
                    "spatialReference": {"wkid": 4326},
                    "x": longitude,
                    "y": latitude,
                },
                separators=(",", ":"),
            ),
            "returnGeometry": "false",
            "geometryType": "esriGeometryPoint",
            "spatialRel": "esriSpatialRelIntersects",
        }
    )
    try:
        data = fetch(
            f"{item['metadataLayerUrl']}/{layer_id}/query?{params}",
            attempts=1,
            timeout=12,
        )
    except (HTTPError, URLError, TimeoutError, OSError):
        return {}
    features = data.get("features") or []
    if not features:
        return {}
    attrs = features[0].get("attributes") or {}
    timestamp = attrs.get("SRC_DATE2")
    capture_date = ""
    if timestamp:
        capture_date = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).date().isoformat()
    return {
        "capture_date": capture_date,
        "provider": attrs.get("NICE_DESC") or "",
        "source": attrs.get("SRC_DESC") or "",
        "resolution_m": attrs.get("SAMP_RES"),
        "accuracy_m": attrs.get("SRC_ACC"),
    }


def distinct_releases(
    longitude: float,
    latitude: float,
    zoom: int,
    items: list[dict],
    item_by_release: dict[int, dict],
    previous_release: dict[int, int | None],
) -> list[dict]:
    column = long2tile(longitude, zoom)
    row = lat2tile(latitude, zoom)
    release_number = items[0]["releaseNum"]
    candidates: list[dict] = []
    seen: set[int] = set()

    while release_number and release_number not in seen:
        seen.add(release_number)
        response = fetch(f"{TILEMAP_ROOT}/{release_number}/{zoom}/{row}/{column}")
        data = response.get("data") or [0]
        selected = response.get("select") or []
        if data[0]:
            changed_release = int(selected[0]) if selected and selected[0] else release_number
            item = item_by_release.get(changed_release)
            if item:
                candidates.append(item)
            release_number = previous_release.get(changed_release)
        else:
            break

    unique_oldest_first: list[tuple[dict, str]] = []
    for item in reversed(candidates):
        digest = hashlib.sha256(fetch(tile_url(item, zoom, row, column), binary=True)).hexdigest()
        if unique_oldest_first and unique_oldest_first[-1][1] == digest:
            continue
        unique_oldest_first.append((item, digest))
    return [
        {**item, "tileSha256": digest}
        for item, digest in reversed(unique_oldest_first)
    ]


def serialize_release(item: dict, meta: dict) -> dict:
    return {
        "release_num": item["releaseNum"],
        "release_date": release_date(item).date().isoformat(),
        "capture_date": meta.get("capture_date", ""),
        "provider": meta.get("provider", ""),
        "source": meta.get("source", ""),
        "resolution_m": meta.get("resolution_m"),
        "accuracy_m": meta.get("accuracy_m"),
        "tile_sha256": item["tileSha256"],
        "tile_url": leaflet_url(item),
    }


def main() -> None:
    with PROJECTS_FILE.open(encoding="utf-8", newline="") as handle:
        projects = list(csv.DictReader(handle))

    config = fetch(CONFIG_URL)
    items = []
    for key, item in config.items():
        if not str(key).isdigit() or not isinstance(item, dict) or "itemTitle" not in item:
            continue
        enriched = dict(item)
        enriched["releaseNum"] = int(key)
        try:
            enriched["releaseDatetime"] = release_date(enriched).timestamp()
        except ValueError:
            continue
        items.append(enriched)
    items.sort(key=lambda item: item["releaseDatetime"], reverse=True)
    item_by_release = {item["releaseNum"]: item for item in items}
    previous_release = {
        item["releaseNum"]: items[index + 1]["releaseNum"] if index + 1 < len(items) else None
        for index, item in enumerate(items)
    }

    point_specs = {}
    for project in projects:
        zoom = 17 if project["cohort_role"] == "xichuan_deep_audit" else 16
        key = (float(project["lon"]), float(project["lat"]), zoom)
        point_specs[key] = key

    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    else:
        cache = {}
    point_releases: dict[tuple[float, float, int], list[dict]] = {}
    lock = threading.Lock()

    for point in point_specs:
        cache_key = "|".join([*(f"{value:.4f}" for value in point[:2]), str(point[2])])
        cached = cache.get(cache_key)
        if cached:
            point_releases[point] = [
                {**item_by_release[int(row["release_num"])], "tileSha256": row["tile_sha256"]}
                for row in cached
                if int(row["release_num"]) in item_by_release
            ]

    def scan(point):
        longitude, latitude, zoom = point
        releases = distinct_releases(
            longitude,
            latitude,
            zoom,
            items,
            item_by_release,
            previous_release,
        )
        with lock:
            point_releases[point] = releases
            cache_key = "|".join([*(f"{value:.4f}" for value in point[:2]), str(point[2])])
            cache[cache_key] = [
                {"release_num": item["releaseNum"], "tile_sha256": item["tileSha256"]}
                for item in releases
            ]
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            CACHE_FILE.write_text(json.dumps(cache, separators=(",", ":")), encoding="utf-8")
        return point, len(releases)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(scan, point) for point in point_specs if point not in point_releases]
        for point in point_specs:
            if point in point_releases:
                print("cached local changes", point, len(point_releases[point]))
        for future in as_completed(futures):
            point, count = future.result()
            print("local changes", point, count)

    metadata_cache: dict[tuple[float, float, int, int], dict] = {}
    metadata_jobs = []
    for (longitude, latitude, zoom), releases in point_releases.items():
        for item in releases:
            metadata_jobs.append(((longitude, latitude, zoom, item["releaseNum"]), item))

    def get_metadata(job):
        key, item = job
        longitude, latitude, zoom, _ = key
        return key, metadata(item, longitude, latitude, zoom)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_metadata, job) for job in metadata_jobs]
        for index, future in enumerate(as_completed(futures), start=1):
            key, value = future.result()
            metadata_cache[key] = value
            if index % 20 == 0 or index == len(futures):
                print("imagery metadata", index, "/", len(futures))

    output = {}
    for project in projects:
        longitude = float(project["lon"])
        latitude = float(project["lat"])
        zoom = 17 if project["cohort_role"] == "xichuan_deep_audit" else 16
        releases = [item for item in point_releases[(longitude, latitude, zoom)] if release_date(item) <= CUTOFF]
        if len(releases) < 2:
            raise RuntimeError(f"Not enough distinct imagery releases for {project['project_id']}")

        signed = datetime.fromisoformat(project["sign_date"]).replace(tzinfo=timezone.utc)
        timed = [
            (item, metadata_cache.get((longitude, latitude, zoom, item["releaseNum"]), {}))
            for item in releases
        ]
        before_candidates = [
            (item, meta)
            for item, meta in timed
            if meta.get("capture_date") and meta["capture_date"] <= signed.date().isoformat()
        ]
        before = max(
            before_candidates,
            key=lambda pair: pair[1]["capture_date"],
            default=None,
        )
        if before is None:
            before = next(
                ((item, meta) for item, meta in timed if release_date(item) < signed),
                (releases[-1], {}),
            )

        after_candidates = [
            (item, meta)
            for item, meta in timed
            if meta.get("capture_date")
            and signed.date().isoformat() < meta["capture_date"] <= CUTOFF.date().isoformat()
            and item["releaseDatetime"] <= CUTOFF.timestamp()
        ]
        after = max(
            after_candidates,
            key=lambda pair: pair[1]["capture_date"],
            default=None,
        )
        pair_type = "post_sign_capture_before_capture_unknown"
        if after is None:
            dated = [(item, meta) for item, meta in timed if meta.get("capture_date")]
            if len({meta["capture_date"] for _, meta in dated}) > 1:
                earliest = min(dated, key=lambda pair: pair[1]["capture_date"])
                latest = max(dated, key=lambda pair: pair[1]["capture_date"])
                before, after = earliest, latest
            else:
                after = next(
                    (
                        (item, meta)
                        for item, meta in timed
                        if item["releaseDatetime"] <= CUTOFF.timestamp()
                        and item["releaseNum"] != before[0]["releaseNum"]
                        and item["tileSha256"] != before[0]["tileSha256"]
                    ),
                    None,
                )
            if after is None:
                raise RuntimeError(f"No distinct cutoff image for {project['project_id']}")
            pair_type = "latest_distinct_image_no_verified_post_sign_capture"

        before_item, before_meta = before
        after_item, after_meta = after
        if (
            before_meta.get("capture_date")
            and before_meta["capture_date"] <= signed.date().isoformat()
            and after_meta.get("capture_date")
            and after_meta["capture_date"] > signed.date().isoformat()
        ):
            pair_type = "acquisition_dates_bracket_signing"
        if before_item["releaseNum"] == after_item["releaseNum"]:
            raise RuntimeError(f"No distinct pair for {project['project_id']}")
        if before_item["tileSha256"] == after_item["tileSha256"]:
            raise RuntimeError(f"Pixel-identical pair for {project['project_id']}")
        pair = [
            serialize_release(before_item, before_meta),
            serialize_release(after_item, after_meta),
        ]

        output[project["project_id"]] = {
            "before": pair[0],
            "after": pair[1],
            "zoom": zoom,
            "comparison_type": pair_type,
            "locally_distinct": pair[0]["tile_sha256"] != pair[1]["tile_sha256"],
            "geometry_precision": project["geometry_precision"],
            "note": "Two releases were selected only after the center tile bytes differed at the display zoom.",
        }

    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT_FILE, len(output))


if __name__ == "__main__":
    main()
