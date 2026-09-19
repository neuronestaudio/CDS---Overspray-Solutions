# -*- coding: utf-8 -*-
"""Fetch real suburb boundaries from OpenStreetMap (via Nominatim), simplify them,
and record centroid, land area and postcode.

Ported from the Ronin build (itself from JED / East Shore). Changes for CDS:
  * a south-east Melbourne bounding box instead of Greater Sydney;
  * a reverse-geocode pass for any suburb the forward search returned without a
    postcode (the forward search only carries one about half the time).

Nominatim usage policy: max 1 request/second, identifying User-Agent, cache the
results. Fetch once and commit the output - the site never calls this at
runtime. Re-running only fills in what is missing.
"""
import json, os, math, time, sys, io, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")  # not a new TextIOWrapper: a second one (on import) closes the first
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from suburb_list import all_targets

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "boundaries.json")
UA = {"User-Agent": "CDS-OverspraySolutions-SuburbPages/1.0 (dion@pndulumdigital.com)"}

# South-east Melbourne, generously: Mulgrave/Boronia to the north-west, Gembrook
# and Tynong to the east, Western Port to the south, Frankston to the west.
# Anything outside is a same-name suburb elsewhere - Beaconsfield (NSW, TAS),
# Clyde (NSW), Emerald (QLD), Seaford (SA), Mulgrave (NSW), Lyndhurst (NSW) and
# Sandhurst (the old name for Bendigo) all have twins.
# The north edge must clear Kilsyth (-37.819) and Lilydale (-37.757): at -37.82 Kilsyth was silently
# rejected as NO MATCH, not reported as an error.
# 40 km ring: Middle Park (144.96E) in the west, Labertouche (145.85E) in the east,
# Yering / Bend of Islands (-37.69) in the north, Jam Jerrup (-38.33) in the south.
BBOX = (144.90, -38.45, 145.98, -37.60)  # west, south, east, north

# Only add an override if a name comes back NO MATCH - a wrong postcode here
# makes the query return nothing at all.
QUERY_OVERRIDES = {}

# Never "industrial" (a named industrial site is not a suburb) and never
# "municipality"/"county" (those are the councils - City of Greater Dandenong,
# Shire of Cardinia, City of Frankston - which contain the suburbs we want).
TYPES = ("suburb", "neighbourhood", "town", "village", "quarter", "city",
         "locality", "city_district", "hamlet")


# ------------------------------------------------------------------ geometry
def perp_dist(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def rdp(pts, eps):
    """Ramer-Douglas-Peucker, iterative so a 4,000-point ring cannot blow the stack."""
    if len(pts) < 3:
        return pts[:]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        dmax, idx = 0.0, i
        for k in range(i + 1, j):
            d = perp_dist(pts[k], pts[i], pts[j])
            if d > dmax:
                dmax, idx = d, k
        if dmax > eps:
            keep[idx] = True
            stack.append((i, idx)); stack.append((idx, j))
    return [p for p, k in zip(pts, keep) if k]


def simplify_ring(ring, eps=0.00018, ndp=5):
    s = rdp([(float(x), float(y)) for x, y in ring], eps)
    if s[0] != s[-1]:
        s.append(s[0])
    out, prev = [], None
    for x, y in s:
        p = [round(x, ndp), round(y, ndp)]
        if p != prev:
            out.append(p); prev = p
    if out[0] != out[-1]:
        out.append(out[0])
    return out


def ring_area(ring):
    a = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]; x2, y2 = ring[i + 1]
        a += float(x1) * float(y2) - float(x2) * float(y1)
    return abs(a) / 2


def rings_of(geom):
    t, c = geom.get("type"), geom.get("coordinates", [])
    polys = [c] if t == "Polygon" else (c if t == "MultiPolygon" else [])
    rings = [p[0] for p in polys if p and len(p[0]) >= 4]
    rings.sort(key=ring_area, reverse=True)
    return rings


def centroid(ring):
    cx = cy = a = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]; x2, y2 = ring[i + 1]
        f = x1 * y2 - x2 * y1
        a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    if a == 0:
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        return [sum(xs) / len(xs), sum(ys) / len(ys)]
    a *= 0.5
    return [round(cx / (6 * a), 6), round(cy / (6 * a), 6)]


def km2(ring, lat):
    return ring_area(ring) * (111.32 ** 2) * math.cos(math.radians(lat))


def in_box(c):
    try:
        s, n, w, e = [float(v) for v in c.get("boundingbox", [])]
    except Exception:
        return False
    cx, cy = (w + e) / 2, (s + n) / 2
    return BBOX[0] <= cx <= BBOX[2] and BBOX[1] <= cy <= BBOX[3]


# ------------------------------------------------------------------ network
def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def fetch(name, slug):
    q = QUERY_OVERRIDES.get(slug, "%s, Victoria, Australia" % name)
    p = urllib.parse.urlencode({
        "q": q, "format": "jsonv2", "polygon_geojson": 1, "addressdetails": 1,
        "limit": 10, "countrycodes": "au"})
    res = get("https://nominatim.openstreetmap.org/search?" + p)
    best = None
    for c in res:
        if not in_box(c):
            continue
        if c.get("geojson", {}).get("type") not in ("Polygon", "MultiPolygon"):
            continue
        if c.get("addresstype") not in TYPES:
            continue
        # prefer the gazetted suburb/town over anything looser
        if best is None or c.get("addresstype") in ("suburb", "town"):
            best = c
            if c.get("addresstype") in ("suburb", "town"):
                break
    return best


def reverse_postcode(lng, lat):
    p = urllib.parse.urlencode({"lat": lat, "lon": lng, "format": "jsonv2",
                                "zoom": 16, "addressdetails": 1})
    r = get("https://nominatim.openstreetmap.org/reverse?" + p)
    return (r.get("address") or {}).get("postcode", "")


def main():
    cache = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    targets = all_targets()
    for i, (region, zone, name, slug) in enumerate(targets, 1):
        if slug in cache and cache[slug].get("ok"):
            cache[slug].update(region=region, zone=zone)
            continue
        try:
            c = fetch(name, slug)
        except Exception as e:
            print("  [%d/%d] %s: ERROR %s" % (i, len(targets), name, e), flush=True)
            cache[slug] = {"ok": False, "name": name, "region": region, "zone": zone, "error": str(e)}
            time.sleep(1.2); continue
        if not c:
            print("  [%d/%d] %s: NO MATCH" % (i, len(targets), name), flush=True)
            cache[slug] = {"ok": False, "name": name, "region": region, "zone": zone, "error": "no-match"}
            time.sleep(1.2); continue
        rings = rings_of(c["geojson"])
        if not rings:
            print("  [%d/%d] %s: NO RINGS" % (i, len(targets), name), flush=True)
            cache[slug] = {"ok": False, "name": name, "region": region, "zone": zone, "error": "no-rings"}
            time.sleep(1.2); continue
        simp = [simplify_ring(r) for r in rings[:3]]
        cen = centroid(simp[0])
        a = c.get("address", {})
        cache[slug] = {
            "ok": True, "name": name, "slug": slug, "region": region, "zone": zone,
            "osm_id": c.get("osm_id"), "addresstype": c.get("addresstype"),
            "display_name": c.get("display_name", ""),
            "postcode": a.get("postcode") or "",
            "centroid": cen,
            "area_km2": round(sum(km2(r, cen[1]) for r in simp), 2),
            "rings": simp,
            "points": sum(len(r) for r in simp),
        }
        print("  [%d/%d] %s: %s %dpts %.2fkm2 pc=%s" % (
            i, len(targets), name, c.get("addresstype"), cache[slug]["points"],
            cache[slug]["area_km2"], cache[slug]["postcode"] or "-"), flush=True)
        if i % 10 == 0:
            json.dump(cache, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
        time.sleep(1.15)

    # ---- postcode pass: reverse-geocode the centroid of anything still blank
    for slug, v in cache.items():
        if v.get("ok") and not v.get("postcode"):
            try:
                v["postcode"] = reverse_postcode(*v["centroid"])
                print("  postcode %s -> %s" % (v["name"], v["postcode"] or "(none)"), flush=True)
            except Exception as e:
                print("  postcode %s: ERROR %s" % (v["name"], e), flush=True)
            time.sleep(1.15)

    json.dump(cache, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
    ok = sum(1 for v in cache.values() if v.get("ok"))
    print("\n%d/%d boundaries -> %s (%d KB)" % (ok, len(targets), OUT, os.path.getsize(OUT) // 1024))
    misses = [v["name"] for v in cache.values() if not v.get("ok")]
    if misses:
        print("MISSES: " + ", ".join(sorted(misses)))
    nopc = [v["name"] for v in cache.values() if v.get("ok") and not v.get("postcode")]
    if nopc:
        print("NO POSTCODE: " + ", ".join(sorted(nopc)))


if __name__ == "__main__":
    main()
