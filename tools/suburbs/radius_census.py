# -*- coding: utf-8 -*-
"""How many gazetted suburbs sit within N km of the Berwick studio?

Pulls every admin_level=9 boundary (Victoria's suburbs/localities - VIC uses 9, not the 10 other states use) in a box around
Berwick from Overpass, then measures centre-to-centre distance from Berwick's own
centroid. Writes radius_census.json and prints the 30 km / 40 km counts, plus the
suburbs inside 40 km that suburb_list.py does not cover yet.

    python radius_census.py
"""
import json, os, sys, io, math, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from suburb_list import all_targets, slugify

UA = {"User-Agent": "CDS-OverspraySolutions-SuburbPages/1.0 (dion@pndulumdigital.com)"}
CACHE = os.path.join(HERE, "overpass-admin9.json")
OUT = os.path.join(HERE, "radius_census.json")

berwick = json.load(open(os.path.join(HERE, "boundaries.json"), encoding="utf-8"))["berwick"]["centroid"]
LNG, LAT = berwick
R_MAX = 42.0  # km - a little past 40 so edge cases are visible
dlat = R_MAX / 110.54
dlng = R_MAX / (111.32 * math.cos(math.radians(LAT)))
BOX = "%.4f,%.4f,%.4f,%.4f" % (LAT - dlat, LNG - dlng, LAT + dlat, LNG + dlng)  # s,w,n,e

Q = """[out:json][timeout:240];
relation["boundary"="administrative"]["admin_level"="9"](%s);
out center tags;""" % BOX


def km(a_lng, a_lat, b_lng, b_lat):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lng - a_lng)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def main():
    if os.path.exists(CACHE):
        res = json.load(open(CACHE, encoding="utf-8"))
    else:
        res, last = None, None
        # the main Overpass instance 504s often enough on a query this size to
        # need a fallback; the mirrors run the same data
        for ep in ("https://overpass-api.de/api/interpreter",
                   "https://overpass.kumi.systems/api/interpreter",
                   "https://maps.mail.ru/osm/tools/overpass/api/interpreter"):
            try:
                req = urllib.request.Request(ep, data=urllib.parse.urlencode({"data": Q}).encode(), headers=UA)
                with urllib.request.urlopen(req, timeout=300) as r:
                    res = json.load(r)
                print("overpass: %s" % ep)
                break
            except Exception as e:
                last = e
                print("overpass: %s failed (%s)" % (ep, e))
        if res is None:
            raise SystemExit("all Overpass endpoints failed: %s" % last)
        json.dump(res, open(CACHE, "w", encoding="utf-8"), separators=(",", ":"))

    rows = {}
    for el in res.get("elements", []):
        t, c = el.get("tags", {}), el.get("center") or {}
        name = t.get("name")
        if not name or "lat" not in c:
            continue
        d = km(LNG, LAT, c["lon"], c["lat"])
        slug = slugify(name)
        if slug not in rows or d < rows[slug]["km"]:
            rows[slug] = {"name": name, "km": round(d, 1), "lng": c["lon"], "lat": c["lat"],
                          "postcode": t.get("postal_code", "")}

    covered = {s for _r, _z, _n, s in all_targets()}
    inside = lambda r: [v for v in rows.values() if v["km"] <= r]
    n30, n40 = inside(30), inside(40)
    json.dump(sorted(rows.values(), key=lambda v: v["km"]), open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("Berwick centroid: %.5f, %.5f" % (LAT, LNG))
    print("gazetted suburbs/localities within 30 km: %d" % len(n30))
    print("gazetted suburbs/localities within 40 km: %d" % len(n40))
    print("already covered by suburb_list.py:        %d" % len(covered))
    print("  of which inside 30 km: %d, inside 40 km: %d"
          % (sum(1 for v in n30 if slugify(v["name"]) in covered),
             sum(1 for v in n40 if slugify(v["name"]) in covered)))
    far = [v for v in rows.values() if slugify(v["name"]) in covered and v["km"] > 40]
    if far:
        print("covered but beyond 40 km: " + ", ".join("%s (%.0f)" % (v["name"], v["km"]) for v in far))
    missing_cov = sorted(covered - set(slugify(v["name"]) for v in rows.values()))
    if missing_cov:
        print("covered but not found as admin_level=9 (name mismatch?): " + ", ".join(missing_cov))
    gap = sorted((v for v in n40 if slugify(v["name"]) not in covered), key=lambda v: v["km"])
    print("\nNOT YET COVERED inside 40 km (%d), nearest first:" % len(gap))
    for v in gap:
        print("  %5.1f km  %s" % (v["km"], v["name"]))


if __name__ == "__main__":
    main()
