"""Build slim Ugarit map data for the Hour-1 labs (public sources only).

The UChicago "Ras Shamra-Ugarit" web map
    https://uchicago.maps.arcgis.com/apps/webappviewer/index.html?id=8bc5cbfe1d13492aa8afe9c9bf2aee4c
is backed by two public, queryable ArcGIS feature layers:

    RSTI_vectors     432 polygons  -> the excavation site plan
    RSTI_find_spots  4757 points   -> tablet find spots (with language, script,
                                      area path, and the OCHRE UUID)

This script downloads both, keeps only the handful of fields the labs use, and
writes two small committable files under ``data/``:

    data/ugarit_site_plan.geojson   polygons: {name, layer} + geometry (WGS84)
    data/ugarit_find_spots.csv      one row per find spot:
                                    name, lon, lat, language, script, area, uuid

Genre is deliberately NOT written here: the labs join UDB genre at run time from
the participant-built ``local_data/udb/texts.parquet`` (see workshop_tools.loader), so no
UDB-derived content is redistributed.

Usage:
    python -m workshop_tools.build_ugarit_map
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SERVICES = "https://services.arcgis.com/ppFhFO7kjyIF441C/arcgis/rest/services"
FIND_SPOTS = f"{SERVICES}/RSTI_find_spots/FeatureServer/0"
SITE_PLAN = f"{SERVICES}/RSTI_vectors/FeatureServer/0"

_HERE = Path(__file__).resolve().parents[1]
DATA = _HERE / "data"

_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def _get(url: str, params: dict) -> dict:
    req = Request(f"{url}?{urlencode(params)}",
                  headers={"User-Agent": "ugarit-workshop/1.0"})
    with urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_all(layer_url: str) -> list[dict]:
    """Page through a feature layer (2000-record limit) as GeoJSON features."""
    step = 2000
    features: list[dict] = []
    offset = 0
    while True:
        data = _get(f"{layer_url}/query", {
            "where": "1=1", "outFields": "*", "outSR": "4326",
            "f": "geojson", "resultOffset": offset, "resultRecordCount": step,
        })
        batch = data.get("features", [])
        features.extend(batch)
        exceeded = data.get("properties", {}).get("exceededTransferLimit")
        if not batch or (len(batch) < step and not exceeded):
            break
        offset += len(batch)
        time.sleep(0.3)
    return features


def _clean(value) -> str:
    """Trim, collapse whitespace, and treat '?'/blank as unknown."""
    s = re.sub(r"\s+", " ", str(value or "")).strip()
    return "" if s in ("", "?") else s


def _area_from_path(path: str) -> str:
    """'.../Ugarit/Ugarit/Royal Palace/Locus 68' -> 'Royal Palace'."""
    parts = [p.strip() for p in re.split(r"[\n/]", str(path or "")) if p.strip()]
    # drop the generic roots, keep the first real place name
    skip = {"Locations & objects", "Ugarit", "Seal catalog"}
    for p in parts:
        if p not in skip:
            return "unknown" if p.lower() == "unknown" else p
    return "unknown"


def build_find_spots() -> int:
    rows = []
    for f in _fetch_all(FIND_SPOTS):
        geom = f.get("geometry")
        if not geom or geom.get("type") != "Point":
            continue
        lon, lat = geom["coordinates"][:2]
        p = f.get("properties", {})
        m = _UUID_RE.search(p.get("UUID") or "")
        rows.append({
            "name": _clean(p.get("Name")),
            "lon": round(lon, 7),
            "lat": round(lat, 7),
            "language": _clean(p.get("Language")) or "unknown",
            "script": _clean(p.get("Script")) or "unknown",
            "area": _area_from_path(p.get("Path")),
            "uuid": m.group(0).lower() if m else "",
        })
    out = DATA / "ugarit_find_spots.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "lon", "lat",
                                           "language", "script", "area", "uuid"])
        w.writeheader()
        w.writerows(rows)
    print(f"  {len(rows)} find spots -> {out}", file=sys.stderr)
    return len(rows)


def build_site_plan() -> int:
    features = []
    for f in _fetch_all(SITE_PLAN):
        p = f.get("properties", {})
        features.append({
            "type": "Feature",
            "geometry": f.get("geometry"),
            "properties": {"name": _clean(p.get("Name")),
                           "layer": _clean(p.get("layer"))},
        })
    fc = {"type": "FeatureCollection",
          "crs": {"type": "name",
                  "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
          "features": features}
    out = DATA / "ugarit_site_plan.geojson"
    out.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    print(f"  {len(features)} site-plan polygons -> {out}", file=sys.stderr)
    return len(features)


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    print("Building Ugarit map data from public ArcGIS layers ...", file=sys.stderr)
    build_find_spots()
    build_site_plan()
    print("Done.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
