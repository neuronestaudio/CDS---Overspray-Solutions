# -*- coding: utf-8 -*-
"""Pull real named places out of OpenStreetMap (Overpass) and assign each one to the
suburb whose gazetted boundary contains it.

Ported from the East Shore build. This is what stops ~160 pages reading as one
template with the name swapped. The
landmarks are facts — the shopping centre, the station, the hospital, the named
industrial estate — and they are the reference points a local would actually use.

Two Overpass requests for the whole of south-east Melbourne, then point-in-polygon
locally against the boundaries we already hold. Run fetch_boundaries.py first.
"""
import json, os, re, sys, io, time, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")  # not a new TextIOWrapper: a second one (on import) closes the first

HERE = os.path.dirname(os.path.abspath(__file__))
BOUNDS = os.path.join(HERE, "boundaries.json")
OUT = os.path.join(HERE, "landmarks.json")
UA = {"User-Agent": "CDS-OverspraySolutions-SuburbPages/1.0 (dion@pndulumdigital.com)"}
ENDPOINT = "https://overpass-api.de/api/interpreter"

# south, west, north, east — the Overpass order
BOX = "-38.45,144.90,-37.60,145.98"  # south-east Melbourne
MAX_PER_SUBURB = 4

# Ranked: a suburb's four landmarks are taken from the top of this order, so the
# shopping centre and the station win over a park.
QUERIES = [
    ("centre", f"""[out:json][timeout:180];
(
  nwr["shop"="mall"]["name"]({BOX});
  nwr["railway"="station"]["name"]({BOX});
  nwr["amenity"="hospital"]["name"]({BOX});
  nwr["amenity"~"^(university|college)$"]["name"]({BOX});
  nwr["landuse"~"^(industrial|commercial|retail)$"]["name"]({BOX});
  nwr["aeroway"="aerodrome"]["name"]({BOX});
);
out center tags;"""),
    ("park", f"""[out:json][timeout:180];
(
  nwr["leisure"="park"]["name"]({BOX});
  nwr["leisure"="nature_reserve"]["name"]({BOX});
);
out center tags;"""),
]


def overpass(q, label):
    cache = os.path.join(HERE, f"overpass-{label}.json")
    if os.path.exists(cache):
        print(f"  {label}: from cache", flush=True)
        return json.load(open(cache, encoding="utf-8"))
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    # overpass-api.de 504s on a box this size often enough to need a fallback
    for ep in (ENDPOINT, "https://overpass.kumi.systems/api/interpreter",
               "https://maps.mail.ru/osm/tools/overpass/api/interpreter"):
        try:
            req = urllib.request.Request(ep, data=data, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r:
                res = json.load(r)
            json.dump(res, open(cache, "w", encoding="utf-8"), separators=(",", ":"))
            return res
        except Exception as e:
            last = e
            print(f"  {label}: {ep} failed ({e})", flush=True)
    raise last


# Franchise outlets are tagged all over the place and are not landmarks anywhere.
BRANDS = {
    "bp", "shell", "ampol", "caltex", "united", "7-eleven", "metro petroleum",
    "coles express", "mobil", "puma", "liberty", "budget petrol",
    "mcdonald's", "kfc", "hungry jack's", "subway", "domino's", "red rooster",
    "woolworths", "coles", "aldi", "iga", "costco", "bunnings", "kmart",
    "target", "big w", "myer", "david jones", "officeworks", "harvey norman",
    "meriton", "mirvac", "stockland", "goodman", "dexus", "home", "muji",
    "chemist warehouse", "jb hi-fi", "spotlight", "anaconda", "rebel",
}

# A named landuse polygon is only a landmark when the name reads like an estate
# or a facility. Without this, every petrol station and strip of shops
# arrives as a "landmark".
ESTATE_WORDS = (
    "park", "estate", "centre", "center", "business", "industrial", "precinct",
    "plaza", "village", "square", "mall", "terminal", "depot", "yard", "works",
    "complex", "hub", "gardens", "quarter", "wharf", "port", "markets",
)

GENERIC = {
    "park", "reserve", "playground", "industrial", "industrial area",
    "commercial", "retail", "business park", "town park", "the park",
    "village green", "central park", "memorial park", "shopping centre",
}


# Misspellings in the OSM name tag, corrected before they reach a page.
SPELLING = {
    "Eumemmerring Bussiness Park": "Eumemmerring Business Park",
}


def kind_and_label(tags):
    """Return (rank, display name) or None to drop the element.

    Rank orders what a suburb's four landmarks are taken from: the shopping
    centre and the station beat a park.
    """
    name = (tags.get("name") or "").strip()
    name = SPELLING.get(name, name)
    if not name or len(name) > 42:
        return None
    low = name.lower()
    if low in BRANDS or low in GENERIC:
        return None

    if tags.get("shop") == "mall":
        return (0, name)
    if tags.get("railway") == "station":
        n = name if "station" in low else f"{name} station"
        # Light rail and metro stops are real, but a suburb's heavy rail station
        # is the one a local gives as the reference point.
        return (3 if tags.get("station") in ("light_rail", "subway") else 1, n)
    if tags.get("amenity") == "hospital":
        return (2, name)
    if tags.get("amenity") in ("university", "college"):
        return (2, name)
    if tags.get("aeroway") == "aerodrome":
        return (2, name)
    if tags.get("landuse") in ("industrial", "commercial", "retail"):
        if not any(w in low for w in ESTATE_WORDS):
            return None
        return (3, name)
    if tags.get("leisure") in ("park", "nature_reserve"):
        # Parks only ever fill a gap, and a bare "<Word> Park" is not a
        # reference point anyone gives.
        if len(name.split()) < 2:
            return None
        return (4, name)
    return None


# Real OSM features that are not reference points a local would give: utilities,
# depots, freeway service centres, codes, single rooms, a street. Found by reading
# the full SE Melbourne output, not guessed.
DROP = re.compile(
    r"depot|terminal|distribution centre|letters centre|gas works|refinery|control centre|"
    r"service centre|mechanical|garden supplies|aged care|lodge|school of|study hub|"
    r"monash house|^emergency$|traffic education|yarning circle|duck pond|nature walk|"
    r"airstrip|^site of|^former |shopping strip|business centre|homeco|home co\b|home co\.|"
    r"home consortium|roshchem|marson crescent|edu kingdom|floral arts|\b[a-z]\d+\b|"
    r"^[a-z]+ precinct$|@|^scope$|woolworths|\bu3a\b|"
    # added with the 40 km ring: council planning names, clinics, coded reserves
    r"local centre|retail precinct|orthodontist|park services|hospice|day surgery|"
    r"rehabilitation|bluecross|heritage river|\bssr\b|^school park$",
    re.I)


# OSM spelling errors that would otherwise print verbatim on a page.
TYPO = {"Bussiness": "Business", "Reservior": "Reservoir"}


def tidy(name):
    for a, b in TYPO.items():
        name = name.replace(a, b)
    return name


def norm(name):
    """Key for spotting two names for one place ('Eden Rise' / 'Eden Rise Shopping
    Centre', 'Belgrave station' / 'Belgrave (Narrow-gauge) station').

    Only 'shopping centre/village' and parentheticals are stripped. Stripping
    'station' or 'plaza' too made 'Clayton station' and 'Clayton Plaza' collide,
    and the station was silently dropped."""
    n = re.sub(r"\(.*?\)", "", name.lower())
    n = re.sub(r"\b(shopping centre|shopping village)\b", "", n)
    return re.sub(r"[^a-z0-9]+", "", n)


def point_of(el):
    if el.get("type") == "node":
        return (el.get("lon"), el.get("lat"))
    c = el.get("center") or {}
    if "lon" in c and "lat" in c:
        return (c["lon"], c["lat"])
    return None


def in_ring(pt, ring):
    x, y = pt
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y):
            xint = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xint:
                inside = not inside
        j = i
    return inside


def main():
    raw = json.load(open(BOUNDS, encoding="utf-8"))
    good = {s: v for s, v in raw.items() if v.get("ok")}
    boxes = {}
    for s, v in good.items():
        xs = [p[0] for r in v["rings"] for p in r]
        ys = [p[1] for r in v["rings"] for p in r]
        boxes[s] = (min(xs), min(ys), max(xs), max(ys))

    found = {s: [] for s in good}
    seen = set()
    for label, q in QUERIES:
        print(f"Overpass: {label} ...", flush=True)
        try:
            res = overpass(q, label)
        except Exception as e:
            print(f"  {label}: FAILED {e}")
            continue
        els = res.get("elements", [])
        print(f"  {len(els)} elements", flush=True)
        for el in els:
            pt = point_of(el)
            if not pt or pt[0] is None:
                continue
            kl = kind_and_label(el.get("tags", {}))
            if not kl:
                continue
            rank, name = kl
            hits = []
            for s, (w, so, e, n) in boxes.items():
                if not (w <= pt[0] <= e and so <= pt[1] <= n):
                    continue
                if any(in_ring(pt, r) for r in good[s]["rings"]):
                    hits.append(s)
            if not hits:
                continue
            # Boundaries in our set can overlap (the CBD region sits over four
            # gazetted suburbs), so the tightest containing polygon is the one
            # that actually describes where the place is.
            s = min(hits, key=lambda t: good[t]["area_km2"])
            key = (s, name)
            if key in seen:
                continue
            seen.add(key)
            found[s].append((rank, name))
        time.sleep(2)

    out = {}
    for s, items in found.items():
        items.sort(key=lambda t: (t[0], len(t[1])))
        picked, names, parks = [], set(), 0
        for rank, name in items:
            name = tidy(name)
            if DROP.search(name):
                continue
            low = norm(name)
            # 'Box Hill Central' / 'Box Hill Central South' / '... North' are one
            # centre: a name that extends an already-picked one is the same place.
            if any(low == x or low.startswith(x) or x.startswith(low) for x in names):
                continue
            if rank == 4:
                if parks >= 1:
                    continue
                parks += 1
            names.add(low)
            picked.append(name)
            if len(picked) >= MAX_PER_SUBURB:
                break
        if picked:
            out[s] = picked

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    have = len(out)
    print(f"\n{have}/{len(good)} suburbs have landmarks -> {OUT}")
    empty = sorted(s for s in good if s not in out)
    if empty:
        print(f"NONE FOUND ({len(empty)}): " + ", ".join(empty))


if __name__ == "__main__":
    main()
