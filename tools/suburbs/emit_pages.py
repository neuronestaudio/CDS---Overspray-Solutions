# -*- coding: utf-8 -*-
"""Render every suburb page, the service-areas hub, the homepage map block and
both sitemaps from boundaries.json (+ landmarks.json if present).

    python emit_pages.py

Suburb pages are ceramic-coating-<slug>.html in the repo root. Each carries
<meta name="x-archetype"> / <meta name="x-suburb"> and PAGE-BODY markers so
tools/verify_area_similarity.py can measure them. Run that after this, always.
"""
import os, re, sys, io, json, math, html, glob
sys.stdout.reconfigure(encoding="utf-8")  # not a new TextIOWrapper: a second one (on import) closes the first
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from suburb_list import REGIONS, ZONES, all_targets, slugify
from assign import archetype_for
from content_pool import ARCHETYPES, pick, pick_one
import shared_pool as SP
import mode_pool as MP

ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = "https://cardetailingsolutions.com.au"  # the live domain since 18 Sep 2026; never the vercel.app host
CSSV = "69"
MAPJSV = "4"
ZONE_COLOUR = {"casey": "#e5484d", "south": "#e8a33d", "east": "#9b7bea",
               "hills": "#3fb67a", "north": "#4aa3d8", "bay": "#22b8c9",
               "outer": "#e0679a", "inner": "#c5d04a"}
ZONE_LABEL = dict(ZONES)
HOOK = {
    "established": "Measured correction and certified coatings for well-kept cars",
    "family": "Swirl removal and long-life protection for family cars",
    "growth": "Construction overspray removal and new-car protection",
    "industrial": "Industrial fallout and overspray removal, then a coating that stops it bonding",
    "urban": "Protection from traffic film, kerbside wear and street parking",
    "bayside": "Salt-air protection for cars that live by the water",
    "hills": "Protection from gum sap, damp and leaf stain",
    "acreage": "Dust-proof protection for acreage cars, utes and 4WDs",
    "rural": "Protection for farm utes and country kilometres",
    "prestige": "Measured multi-stage correction and certified coatings for prestige cars",
    "inner": "Swirl removal and coating for apartment and street-parked cars",
    "valley": "Protection from gravel dust, spray drift and highway kilometres",
}

# ------------------------------------------------------------------ data
RAW = json.load(open(os.path.join(HERE, "boundaries.json"), encoding="utf-8"))
LM_PATH = os.path.join(HERE, "landmarks.json")
LANDMARKS = json.load(open(LM_PATH, encoding="utf-8")) if os.path.exists(LM_PATH) else {}

REGION_OF, ZONE_OF, ORDER = {}, {}, []
for region, zone, name, slug in all_targets():
    REGION_OF[slug], ZONE_OF[slug] = region, zone
    ORDER.append(slug)
RECS = {s: RAW[s] for s in ORDER if RAW.get(s, {}).get("ok")}
MISSING = [s for s in ORDER if s not in RECS]


def haversine(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    dp, dl = p2 - p1, math.radians(b[0] - a[0])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


STUDIO = RECS["berwick"]["centroid"]
for s, r in RECS.items():
    r["km"] = round(haversine(r["centroid"], STUDIO) / 1000)


def neighbours_for(slug, want=6):
    """True polygon adjacency first (rings within 150 m), topped up with the
    nearest centroids - most suburbs only border two or three others *within our
    own list*."""
    me = RECS[slug]
    mine = me["rings"][0]
    adjacent, others = [], []
    for o_slug, o in RECS.items():
        if o_slug == slug:
            continue
        d = haversine(me["centroid"], o["centroid"])
        if d > 16000:
            continue
        touching = False
        ring = o["rings"][0]
        for p in mine[::2]:
            for q in ring[::2]:
                if haversine(p, q) < 150:
                    touching = True
                    break
            if touching:
                break
        (adjacent if touching else others).append((d, o_slug))
    adjacent.sort(); others.sort()
    out = [s for _d, s in adjacent][:want]
    for _d, s in others:
        if len(out) >= want:
            break
        if s not in out:
            out.append(s)
    return out


def esc(s):
    return html.escape(s, quote=True)


def fill(t, r):
    return (t.replace("{suburb}", r["name"]).replace("{pc}", r.get("postcode") or "")
             .replace("{km}", str(r["km"])))


def strip_ents(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def join_names(names):
    names = [esc(n) for n in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


# ------------------------------------------------------------------ site chrome
NAVDRAWER = FOOTER = EXPLORER_JS = ""


def load_chrome():
    """Lift the shared nav/drawer/footer off a hand-built page. Called from main()
    after ensure_area_links(), so generated pages inherit the 'Areas' nav link."""
    global NAVDRAWER, FOOTER, EXPLORER_JS
    src = open(os.path.join(ROOT, "paint-correction-melbourne.html"), encoding="utf-8").read()
    NAVDRAWER = re.search(r"<body>\s*(.*?)\s*<header class=\"lp-hero", src, re.S).group(1)
    FOOTER = re.search(r"(<footer class=\"footer\">.*?</footer>)", src, re.S).group(1)
    if "Epping" in NAVDRAWER + FOOTER:
        raise SystemExit("site chrome still says Epping - run the Berwick sweep first")
    if "service-areas.html" not in NAVDRAWER:
        raise SystemExit("site chrome has no Areas link - ensure_area_links() did not run")
    EXPLORER_JS = open(os.path.join(HERE, "explorer.js"), encoding="utf-8").read()


ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
ACTIONS = ('<div class="lp-actions"><a href="index.html#contact" class="btn btn-primary btn-lg">'
           'Get a free quote ' + ARROW + '</a><a href="tel:0410939700" class="btn btn-ghost btn-lg">'
           'Call 0410 939 700</a></div>')
PIN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
       'stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px;'
       'vertical-align:-2px;margin-right:5px"><path d="M12 22s8-4.5 8-11a8 8 0 1 0-16 0c0 '
       '6.5 8 11 8 11z"/><circle cx="12" cy="11" r="3"/></svg>')


def head(title, desc, canonical, ld, extra_meta="", nav=None):
    lds = "\n".join('<script type="application/ld+json">%s</script>'
                    % json.dumps(x, ensure_ascii=False) for x in ld)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0a0a0c">
{extra_meta}<link rel="canonical" href="{BASE}/{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}/{canonical}">
<meta property="og:image" content="{BASE}/assets/img/logo-cds-ceramic.png">
<link rel="shortcut icon" href="assets/img/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://tile.openstreetmap.org" crossorigin>
<link rel="stylesheet" href="css/styles.css?v={CSSV}">
{lds}
</head>
<body>
{nav or NAVDRAWER}"""


def provider():
    return {"@type": "LocalBusiness", "name": "CDS · Overspray Solutions",
            "telephone": "+61410939700", "priceRange": "$$",
            "address": {"@type": "PostalAddress", "addressLocality": "Berwick",
                        "addressRegion": "VIC", "postalCode": "3806", "addressCountry": "AU"}}


# ------------------------------------------------------------------ suburb page
def suburb_page(slug):
    r = RECS[slug]
    n, pc, km = r["name"], r.get("postcode") or "", r["km"]
    arch = archetype_for(n)
    A = ARCHETYPES[arch]
    region, zone = REGION_OF[slug], ZONE_OF[slug]
    ps = "ceramic-coating-" + slug

    title = "Ceramic Coating %s%s | Mobile &amp; In-Studio &mdash; CDS" % (
        n, (" " + pc) if pc else "")
    where = ("mobile across %s or at our studio right here" % n) if km == 0 else (
        "mobile in %s or at our Berwick studio, about %d km away" % (n, km))
    desc = "%s in %s%s. Certified GYEON &amp; ONYX coatings, owner-operated, %s." % (
        HOOK[arch], n, (" " + pc) if pc else "", where)

    lede = fill(pick_one(SP.LEDES, slug, "lede"), r)
    if km == 0:
        lede = ("Ceramic coating, paint correction and paint protection in Berwick %s &mdash; mobile, at "
                "your home or workplace, or at the CDS studio right here. Owner-operated, certified "
                "GYEON and ONYX." % pc)
    intro = fill(pick_one(A["intros"], slug, "intro"), r)
    if km == 0:
        intro = ("Berwick is home. The CDS studio is here and Andy is mobile as well, so a Berwick car "
                 "can be done in your own garage or dropped a few minutes up the road. "
                 + intro)
    owner = fill(pick_one(SP.OWNER, slug, "owner"), r)
    conds = pick(A["conditions"], 4, slug, "cond")
    # Mobile or studio is the first thing anyone asks, so it is pinned - and built from
    # three rotating parts so it does not become the block every page shares verbatim.
    mode_a = " ".join([MP.OPEN_HOME if km == 0 else pick_one(MP.OPEN, slug, "mo"),
                       MP.CORE[arch], pick_one(MP.CLOSE, slug, "mc")])
    faqs = [(fill(pick_one(MP.QUESTIONS, slug, "mq"), r), fill(mode_a, r))]
    faqs += [(fill(q, r), fill(a, r)) for q, a in pick(A["faqs"], 3, slug, "faq")]
    steps = pick_one(SP.PROCESS, slug, "proc")
    svc = pick(SP.SERVICES, 7, slug, "svc")
    near = neighbours_for(slug)
    lms = LANDMARKS.get(slug, [])[:3]

    hs = lambda pool, salt: fill(pick_one(pool, slug, salt), r)
    h_local, h_cond = hs(SP.H_LOCAL, "hl"), hs(SP.H_COND, "hc")
    h_serv, h_proc = hs(SP.H_SERV, "hs"), hs(SP.H_PROC, "hp")
    h_faq, h_near, cta = hs(SP.H_FAQ, "hf"), hs(SP.H_NEAR, "hn"), hs(SP.CTA, "cta")

    stats = ['<span>Postcode <b>%s</b></span>' % pc] if pc else []
    stats += ['<span>Area <b>%s</b></span>' % esc(region),
              '<span>Land area <b>%s km&#178;</b></span>' % r["area_km2"]]
    stats.append('<span><b>Mobile</b> or in-studio</span>')
    stats.append('<span><b>Our studio</b> is in %s</span>' % n if km == 0
                 else '<span><b>~%d km</b> from our Berwick studio</span>' % km)

    lm_line = ""
    if lms:
        lm_line = ('<p class="sb-lm">Around %s.</p>' % join_names(lms))

    cond_html = "".join('<div class="sb-issue reveal"%s><h3>%s</h3><p>%s</p></div>'
                        % (' data-d="%d"' % (i % 3) if i else "", t, fill(b, r))
                        for i, (t, b) in enumerate(conds))
    step_html = "".join('<div class="sb-step reveal"%s><b>%s</b><h3>%s</h3><p>%s</p></div>'
                        % (' data-d="%d"' % (i % 3) if i else "", a, b, c)
                        for i, (a, b, c) in enumerate(steps))
    faq_html = "".join('<details class="sb-faq reveal"><summary>%s</summary><p>%s</p></details>'
                       % (q, a) for q, a in faqs)
    svc_html = '<div class="chips">' + "".join('<a href="%s">%s</a>' % s for s in svc) + "</div>"
    near_html = "".join('<a href="ceramic-coating-%s.html">%s</a>' % (x, esc(RECS[x]["name"])) for x in near)
    near_html += '<a class="all" href="service-areas.html">All %d service areas &rarr;</a>' % len(RECS)

    geo = {"type": "Feature", "properties": {"name": n},
           "geometry": {"type": "MultiPolygon", "coordinates": [[ring] for ring in r["rings"]]}}
    xs = [p[0] for ring in r["rings"] for p in ring]; ys = [p[1] for ring in r["rings"] for p in ring]
    bbox = [round(min(xs), 5), round(min(ys), 5), round(max(xs), 5), round(max(ys), 5)]
    geo_attr = esc(json.dumps(geo, separators=(",", ":")))
    bbox_attr = esc(json.dumps(bbox))

    ld = [
        {"@context": "https://schema.org", "@type": "Service",
         "serviceType": "Mobile and in-studio ceramic coating, paint correction and paint protection",
         "name": "Ceramic Coating %s" % n, "url": "%s/%s.html" % (BASE, ps),
         "areaServed": {"@type": "City", "name": n + ((" " + pc) if pc else ""),
                        "containedInPlace": {"@type": "AdministrativeArea", "name": "Victoria, Australia"}},
         "provider": provider()},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/index.html"},
            {"@type": "ListItem", "position": 2, "name": "Service Areas", "item": BASE + "/service-areas.html"},
            {"@type": "ListItem", "position": 3, "name": n, "item": "%s/%s.html" % (BASE, ps)}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip_ents(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip_ents(a)}} for q, a in faqs]},
    ]
    meta = ('<meta name="x-archetype" content="%s">\n<meta name="x-suburb" content="%s">\n' % (arch, slug))

    return head(title, desc, ps + ".html", ld, meta) + f"""
<!--PAGE-BODY-START-->
<header class="lp-hero textured">
  <div class="wrap">
    <nav class="lp-crumb" aria-label="Breadcrumb"><a href="index.html">Home</a><i>/</i><a href="service-areas.html">Service Areas</a><i>/</i><a href="service-areas.html#{slugify(region)}">{esc(region)}</a><i>/</i><span>{esc(n)}</span></nav>
    <span class="eyebrow">{PIN}{esc(n)}{(' ' + pc) if pc else ''} &middot; {esc(ZONE_LABEL[zone])}</span>
    <h1 class="lp-h1">Ceramic Coating <em>{esc(n)}</em></h1>
    <p class="lp-lede">{lede}</p>
    {ACTIONS}
    <div class="sb-stats reveal">{''.join(stats)}</div>
  </div>
</header>

<section class="section">
  <div class="wrap">
    <div class="sb-split">
      <div class="sb-copy reveal">
        <h2 class="h-sec" style="font-size:clamp(1.7rem,3.2vw,2.4rem);margin-bottom:18px">{h_local}</h2>
        <p>{intro}</p>
        <p>{owner}</p>
      </div>
      <figure class="suburb-map reveal">
        <div class="suburb-map__canvas" data-geo="{geo_attr}" data-bbox="{bbox_attr}" data-colour="#e11d2a"
             role="img" aria-label="Map showing the boundary of {esc(n)}{(' ' + pc) if pc else ''}"></div>
        <figcaption><b>{esc(n)}{(' ' + pc) if pc else ''}</b> &mdash; the gazetted suburb boundary.
        Boundary and map data &copy; OpenStreetMap contributors.</figcaption>
        {lm_line}
      </figure>
    </div>
  </div>
</section>

<section class="section" style="background:var(--bg-2);border-block:1px solid var(--line)">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="eyebrow">{esc(A['label'])}</span>
      <h2 class="h-sec">{h_cond}</h2>
    </div>
    <div class="sb-issues">{cond_html}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="eyebrow">Services</span>
      <h2 class="h-sec">{h_serv}</h2>
    </div>
    <div class="lp-related" style="margin-top:22px">{svc_html}</div>
  </div>
</section>

<section class="section" style="background:var(--bg-2);border-block:1px solid var(--line)">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="eyebrow">The process</span>
      <h2 class="h-sec">{h_proc}</h2>
    </div>
    <div class="sb-steps">{step_html}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="eyebrow">FAQs</span>
      <h2 class="h-sec">{h_faq}</h2>
    </div>
    <div class="sb-faqs">{faq_html}</div>
  </div>
</section>

<section class="section" style="background:var(--bg-2);border-block:1px solid var(--line)">
  <div class="wrap">
    <div class="sec-head reveal">
      <h2 class="h-sec" style="font-size:clamp(1.5rem,3vw,2.1rem)">{h_near}</h2>
    </div>
    <div class="sb-near reveal">{near_html}</div>
  </div>
</section>

<section class="lp-ctaband">
  <div class="wrap"><div class="in">
    <h2>{cta}</h2>
    {ACTIONS}
  </div></div>
</section>
<!--PAGE-BODY-END-->
{FOOTER}
<script src="js/page.js?v=10"></script>
<script src="js/suburb-map.js?v={MAPJSV}"></script>
</body>
</html>"""


# ------------------------------------------------------------------ explorer (overview map + directory)
ICON_SEARCH = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>')
ICON_LOCATE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.4"/>'
               '<path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>')


def explorer(eps=0.0006):
    """The suburb explorer: toolbar, area chips, vector map with distance rings, and a
    directory of plain links. Returns (markup, facts)."""
    from fetch_boundaries import rdp
    items = [(s, RECS[s]) for s in ORDER if s in RECS]
    mn = [1e9, 1e9]; mx = [-1e9, -1e9]
    simp = {}
    for s, r in items:
        rs = []
        for ring in r["rings"]:
            pts = rdp([tuple(p) for p in ring], eps)
            if len(pts) >= 4:
                rs.append(pts)
        simp[s] = rs or [r["rings"][0]]
        for ring in simp[s]:
            for x, y in ring:
                mn[0] = min(mn[0], x); mn[1] = min(mn[1], y)
                mx[0] = max(mx[0], x); mx[1] = max(mx[1], y)
    kx = math.cos(math.radians((mn[1] + mx[1]) / 2))
    PAD, W = 16, 720
    sc = (W - PAD * 2) / ((mx[0] - mn[0]) * kx)
    H = round((mx[1] - mn[1]) * sc + PAD * 2)
    px = lambda x: round(((x - mn[0]) * kx * sc + PAD) * 10) / 10
    py = lambda y: round(((mx[1] - y) * sc + PAD) * 10) / 10
    ppk = sc / 110.95                      # viewBox units per km (x and y agree to <1%)

    region_names = [reg for reg, _z, _n in REGIONS]
    zone_keys = [z for z, _ in ZONES]
    shapes = []
    for s, r in items:
        box = [1e9, 1e9, -1e9, -1e9]; parts = []
        for ring in simp[s]:
            seg = []
            for i, (x, y) in enumerate(ring):
                X, Y = px(x), py(y)
                box = [min(box[0], X), min(box[1], Y), max(box[2], X), max(box[3], Y)]
                seg.append(("M" if i == 0 else "L") + "%s %s" % (X, Y))
            parts.append("".join(seg) + "Z")
        c = r["centroid"]
        shapes.append(dict(slug=s, name=r["name"], pc=r.get("postcode") or "", zone=ZONE_OF[s],
                           region=REGION_OF[s], area=r["area_km2"], km=r["km"], d="".join(parts),
                           cx=px(c[0]), cy=py(c[1]), box=box))
    # biggest first, so small suburbs paint (and click) on top of large ones
    shapes.sort(key=lambda t: (t["box"][2] - t["box"][0]) * (t["box"][3] - t["box"][1]), reverse=True)
    index = {t["slug"]: i for i, t in enumerate(shapes)}

    zbox = {"all": [PAD, PAD, W - PAD, H - PAD]}
    for t in shapes:
        z = zbox.setdefault(t["zone"], [1e9, 1e9, -1e9, -1e9])
        z[:] = [min(z[0], t["box"][0]), min(z[1], t["box"][1]), max(z[2], t["box"][2]), max(z[3], t["box"][3])]
    zbox = {k: [round(v, 1) for v in b] for k, b in zbox.items()}
    counts = {z: sum(1 for t in shapes if t["zone"] == z) for z in zone_keys}

    sx_, sy_ = px(STUDIO[0]), py(STUDIO[1])
    max_km = max(t["km"] for t in shapes)
    rings = [k for k in (10, 20, 30, 40, 50) if k <= max_km + 2]
    ring_svg = []
    for k in rings:
        rad = round(k * ppk, 1)
        ring_svg.append('<circle cx="%s" cy="%s" r="%s"/>' % (sx_, sy_, rad))
        for lx, ly in ((sx_, sy_ - rad), (sx_, sy_ + rad), (sx_ + rad, sy_), (sx_ - rad, sy_)):
            if 14 <= lx <= W - 14 and 12 <= ly <= H - 12:
                ring_svg.append('<text x="%s" y="%s" text-anchor="middle" dominant-baseline="middle">%d KM</text>'
                                % (round(lx, 1), round(ly, 1), k))
                break

    subs = "".join('<a class="sx__sub" href="ceramic-coating-%s.html" data-i="%d" data-z="%s" aria-label="%s%s">'
                   '<path d="%s"/></a>' % (t["slug"], i, t["zone"], esc(t["name"]),
                                           (" " + t["pc"]) if t["pc"] else "", t["d"])
                   for i, t in enumerate(shapes))
    pin = lambda cls, x, y, label, hidden: (
        '<g class="sx__pin %s"%s style="transform:translate(%spx,%spx) scale(var(--k,1))">'
        '<circle class="pulse" r="7"/><circle class="core" r="5"/><text x="11" y="4">%s</text></g>'
        % (cls, " hidden" if hidden else "", x, y, label))

    chips = ['<button type="button" class="sx__zone is-on" data-zone="all" aria-pressed="true">'
             '<i class="sx__dot sx__dot--all" aria-hidden="true"></i>All areas <b>%d</b></button>' % len(shapes)]
    chips += ['<button type="button" class="sx__zone" data-zone="%s" aria-pressed="false"><i class="sx__dot" '
              'style="--z:var(--z-%s)" aria-hidden="true"></i>%s <b>%d</b></button>' % (z, z, esc(lab), counts[z])
              for z, lab in ZONES]

    regs = []
    for region, zone, names in REGIONS:
        members = sorted((nm for nm in names if slugify(nm) in index), key=str.lower)
        if not members:
            continue
        lis = "".join('<li><a href="ceramic-coating-%s.html" data-i="%d">%s%s</a></li>'
                      % (slugify(nm), index[slugify(nm)], esc(nm),
                         (" <small>%s</small>" % shapes[index[slugify(nm)]]["pc"]) if shapes[index[slugify(nm)]]["pc"] else "")
                      for nm in members)
        regs.append('<details class="sx__reg" open data-z="%s" data-n="%d"><summary><i class="sx__dot" '
                    'style="--z:var(--z-%s)" aria-hidden="true"></i><span class="t">%s</span><b>%d</b></summary>'
                    '<ul>%s</ul></details>' % (zone, len(members), zone, esc(region), len(members), lis))

    data = {"z": [[z, lab] for z, lab in ZONES], "r": region_names,
            "s": [[t["name"], t["pc"], zone_keys.index(t["zone"]), region_names.index(t["region"]),
                   t["area"], t["km"], t["cx"], t["cy"]] for t in shapes]}
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    n = len(shapes)
    markup = (
        '<div class="sx reveal" data-zone="all" data-w="%d" data-h="%d" data-ppk="%.4f" data-proj="%.6f,%.6f,%.6f,%.4f,%d" '
        'data-studio="%s,%s" data-zones=\'%s\'>'
        % (W, H, ppk, mn[0], mx[1], kx, sc, PAD, sx_, sy_, json.dumps(zbox, separators=(",", ":")))
        + '<div class="sx__bar"><div class="sx__search">' + ICON_SEARCH
        + '<input type="search" role="combobox" aria-label="Search suburbs or postcodes" aria-expanded="false" '
          'aria-controls="sx-results" aria-autocomplete="list" autocomplete="off" spellcheck="false" '
          'placeholder="Search %d suburbs or a postcode&hellip;">' % n
        + '<button type="button" class="sx__clear" aria-label="Clear search" hidden>&times;</button>'
          '<ul class="sx__results" id="sx-results" role="listbox" aria-label="Matching suburbs" hidden></ul></div>'
        + '<button type="button" class="sx__locate" aria-label="Find the suburb I am in">' + ICON_LOCATE
        + '<span>Near me</span></button></div>'
        + '<div class="sx__zones" role="group" aria-label="Filter by area">' + "".join(chips) + '</div>'
        + '<div class="sx__body"><div class="sx__map"><div class="sx__stage">'
        + '<svg viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid meet" role="group" aria-label="Map of the %d '
          'south-east Melbourne suburbs CDS services, drawn from their gazetted boundaries">' % (W, H, n)
        + '<g class="sx__world"><g class="sx__rings">' + "".join(ring_svg) + '</g>' + subs
        + '<g class="sx__labels"></g>' + pin("sx__studio", sx_, sy_, "CDS studio", False)
        + pin("sx__me", 0, 0, "You", True) + '</g></svg>'
        + '<div class="sx__tip" role="tooltip" hidden></div>'
        + '<div class="sx__ctls" aria-label="Map zoom"><button type="button" data-act="in" aria-label="Zoom in">+</button>'
          '<button type="button" data-act="out" aria-label="Zoom out">&minus;</button>'
          '<button type="button" data-act="reset" aria-label="Reset the map">&#8634;</button></div>'
        + '<div class="sx__legend">Rings every 10 km from our Berwick studio</div></div>'
        + '<div class="sx__card" aria-live="polite" hidden><div class="sx__card-top"><span class="sx__card-zone"></span>'
          '<button type="button" class="sx__close" aria-label="Close">&times;</button></div>'
          '<strong class="sx__card-name"></strong><p class="sx__card-meta"></p><div class="sx__near"></div>'
          '<div class="sx__card-cta"><a class="btn btn-primary sx__card-open" href="service-areas.html"><span>Open</span> '
        + ARROW + '</a><a class="btn btn-ghost" href="index.html#contact">Get a quote</a></div></div></div>'
        + '<div class="sx__panel"><div class="sx__panel-head"><span class="sx-kick">Every suburb, by area</span>'
          '<span class="sx__count">%d suburbs</span></div><div class="sx__dir">' % n + "".join(regs) + '</div></div></div>'
        + '<script type="application/json" class="sx__data">' + data_json + '</script></div>')
    facts = {"n": n, "zones": len(ZONES), "regions": len(regs), "radius": int(max_km // 10 * 10), "max_km": max_km}
    return markup, facts


def explorer_head(facts, h2):
    return ('<div class="sx-head reveal"><div class="sx-head__copy"><span class="eyebrow">Service areas</span>'
            '<h2 class="h-sec">%s</h2><p class="lede">Search your suburb, tap &ldquo;near me&rdquo;, or pick it on the map. We come to you, or you bring the car to our Berwick studio. '
            'Every one of the %d suburbs has its own page, drawn from its real gazetted boundary.</p></div>'
            '<ul class="sx-stats" aria-label="Coverage"><li><b>%d</b><span>Suburbs</span></li><li><b>%d</b><span>Areas</span></li>'
            '<li><b>%d<em>km</em></b><span>Around Berwick</span></li></ul></div>'
            % (h2, facts["n"], facts["n"], facts["zones"], facts["radius"]))


def region_grid():
    """service-areas.html only: every suburb by region, always visible, with the
    #region anchors the suburb-page breadcrumbs point at."""
    out = []
    for region, zone, names in REGIONS:
        items = sorted(((slugify(nm), nm) for nm in names if slugify(nm) in RECS), key=lambda t: t[1].lower())
        lis = "".join('<li><a href="ceramic-coating-%s.html">%s</a></li>' % (s, esc(nm)) for s, nm in items)
        out.append('<div class="sx-grid__col" id="%s"><h3>%s <span>%d</span></h3><ul>%s</ul></div>'
                   % (slugify(region), esc(region), len(items), lis))
    return '<div class="sx-grid">' + "".join(out) + '</div>'


def map_css():
    base = open(os.path.join(HERE, "explorer_base.css"), encoding="utf-8").read()
    zones = [z for z, _ in ZONES]
    base = base.replace("/*ZONEVARS*/", "".join("--z-%s:%s;" % (z, ZONE_COLOUR[z]) for z in zones) + "--z:var(--z-casey);")
    extra = ['.sx__sub[data-z="%s"]{--z:var(--z-%s)}' % (z, z) for z in zones]
    extra.append(".sx__dot--all{background:conic-gradient(%s)}" % ",".join("var(--z-%s)" % z for z in zones + zones[:1]))
    extra.append(",\n".join('.sx[data-zone="%s"] .sx__sub:not([data-z="%s"]) path' % (z, z) for z in zones) + "{opacity:.12}")
    extra.append(",\n".join('.sx[data-zone="%s"] .sx__lbl:not([data-z="%s"])' % (z, z) for z in zones) + "{opacity:0!important}")
    return base.rstrip() + "\n" + "\n".join(extra) + "\n"


def home_ld(facts):
    """The homepage's business schema. It had none at all before 19 Sep 2026."""
    return {"@context": "https://schema.org", "@type": "AutomotiveBusiness",
            "@id": BASE + "/#business", "name": "CDS · Overspray Solutions",
            "alternateName": "Car Detailing Solutions",
            "description": ("Owner-operated ceramic coating, paint correction, paint protection and overspray removal. "
                            "Mobile across Melbourne's south-east, and from our studio in Berwick."),
            "url": BASE + "/", "telephone": "+61410939700", "email": "info@cardetailingsolutions.com.au",
            "image": BASE + "/assets/img/logo-cds-ceramic.png", "logo": BASE + "/assets/img/logo-mark.png",
            "priceRange": "$$",
            "address": {"@type": "PostalAddress", "addressLocality": "Berwick", "addressRegion": "VIC",
                        "postalCode": "3806", "addressCountry": "AU"},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                           "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                                                         "Saturday", "Sunday"],
                                           "opens": "07:00", "closes": "19:00"}],
            "areaServed": {"@type": "GeoCircle",
                           "geoMidpoint": {"@type": "GeoCoordinates", "latitude": round(STUDIO[1], 4),
                                           "longitude": round(STUDIO[0], 4)},
                           "geoRadius": str(facts["radius"] * 1000)},
            "hasMap": BASE + "/service-areas.html",
            "knowsAbout": ["Ceramic coating", "Graphene coating", "Paint correction", "Paint protection",
                           "Overspray removal", "Industrial fallout removal"]}


# ------------------------------------------------------------------ hub page
def hub_page(sx, facts):
    n = facts["n"]
    ld = [{"@context": "https://schema.org", "@type": "ItemList",
           "name": "CDS service areas", "numberOfItems": n,
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": RECS[s]["name"],
                                "url": "%s/ceramic-coating-%s.html" % (BASE, s)}
                               for i, s in enumerate(x for x in ORDER if x in RECS)]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/index.html"},
              {"@type": "ListItem", "position": 2, "name": "Service Areas", "item": BASE + "/service-areas.html"}]}]
    desc = ("Ceramic coating, paint correction and overspray removal across %d suburbs of Melbourne&rsquo;s "
            "south-east &mdash; mobile, or at our Berwick studio. Search your suburb or find it on the map." % n)
    nav = NAVDRAWER.replace('<a href="service-areas.html">Areas</a>',
                            '<a href="service-areas.html" aria-current="page">Areas</a>', 1)
    return head("Service Areas | Ceramic Coating Across Melbourne&rsquo;s South-East &mdash; CDS",
                desc, "service-areas.html", ld, nav=nav) + f"""
<header class="lp-hero textured">
  <div class="wrap">
    <nav class="lp-crumb" aria-label="Breadcrumb"><a href="index.html">Home</a><i>/</i><span>Service Areas</span></nav>
    <span class="eyebrow">{PIN}Berwick 3806 &middot; Melbourne&rsquo;s south-east</span>
    <h1 class="lp-h1">Areas we <em>service</em></h1>
    <p class="lp-lede">{n} suburbs, from Berwick out to St Kilda, Kew and Eltham in one direction and Longwarry,
    Lang Lang and the Yarra Valley in the other &mdash; every suburb within {facts['radius']} km of Berwick.
    We come to you, or you bring the car to our Berwick studio. Each suburb has its own page, drawn from its
    real gazetted boundary.</p>
    {ACTIONS}
  </div>
</header>
<section class="section sx-sec textured" id="map">
  <div class="wrap">
    {explorer_head(facts, 'Find your <em>suburb</em>.')}
    {sx}
  </div>
</section>
<section class="section" style="background:var(--bg-2);border-block:1px solid var(--line)">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="eyebrow">Every suburb</span>
      <h2 class="h-sec">All {n} service areas, by region.</h2>
    </div>
    {region_grid()}
  </div>
</section>
<section class="lp-ctaband">
  <div class="wrap"><div class="in">
    <h2>Don&rsquo;t see your suburb? Ask anyway.</h2>
    {ACTIONS}
  </div></div>
</section>
{FOOTER}
<script src="js/page.js?v=10"></script>
<script>
{EXPLORER_JS}</script>
</body>
</html>"""


def home_block(sx, facts):
    return f"""<!--SAM-START-->
<!-- ============ SERVICE AREAS (suburb explorer: generated by tools/suburbs/emit_pages.py) ============ -->
<section class="section sx-sec textured" id="areas">
  <div class="wrap">
    {explorer_head(facts, 'Find your <em>suburb</em>.')}
    {sx}
    <p class="sx-more reveal"><a href="service-areas.html">Open the full service-areas page, with every suburb by region &rarr;</a></p>
  </div>
</section>
<script>
{EXPLORER_JS}</script>
<!--SAM-END-->

"""


# ------------------------------------------------------------------ site-wide nav
def ensure_area_links():
    """Put 'Areas' in the primary nav, the mobile drawer and the footer of every page.
    Idempotent. Generated pages inherit it from the chrome lifted afterwards."""
    touched = 0
    for p in glob.glob(os.path.join(ROOT, "*.html")):
        s = t = open(p, encoding="utf-8").read()

        def nav(m):
            b = m.group(0)
            if "service-areas.html" in b:
                return b
            return re.sub(r'(<a href="about\.html"[^>]*>About</a>)',
                          r'\1\n      <a href="service-areas.html">Areas</a>', b, count=1)
        t = re.sub(r'<nav class="nav-links".*?</nav>', nav, t, count=1, flags=re.S)

        # the About d-link only ever appears inside the mobile drawer
        if 'class="d-link" href="service-areas.html"' not in t:
            t = t.replace('<a class="d-link" href="about.html">About</a>',
                          '<a class="d-link" href="about.html">About</a>\n'
                          '  <a class="d-link" href="service-areas.html">Service Areas</a>', 1)

        def foot(m):
            if "service-areas.html" in m.group(1):
                return m.group(0)
            return m.group(1) + '<a href="service-areas.html">Service areas</a>' + m.group(2)
        t = re.sub(r'(<div class="foot-col">\s*<h4>Services</h4>.*?)(\s*</div>)', foot, t, count=1, flags=re.S)
        if t != s:
            open(p, "w", encoding="utf-8").write(t); touched += 1
    return touched


# ------------------------------------------------------------------ sitemaps
def sitemap_xml():
    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
    pages = [p for p in pages if p not in ("bay-scroll.html",)]
    sub = {"ceramic-coating-%s.html" % s for s in RECS}

    def prio(f):
        if f == "index.html": return "1.0"
        if f == "service-areas.html": return "0.9"
        if f in sub: return "0.6"
        if f in ("about.html", "sitemap.html", "warranties.html", "product-tds.html"): return "0.7"
        return "0.8"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += ['  <url><loc>%s/%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>'
              % (BASE, f, prio(f)) for f in pages]
    lines.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return len(pages)


def sitemap_html():
    p = os.path.join(ROOT, "sitemap.html")
    s = open(p, encoding="utf-8").read()
    # drop every previous service-area column (old north-side sets + earlier SEO columns)
    s = re.sub(r'<!--SEOCOLS-->.*?<!--/SEOCOLS-->\s*', "", s, flags=re.S)
    s = re.sub(r'\s*<nav class="sm-col"[^>]*aria-label="(?:Service Areas|More Service Areas)"[^>]*>.*?</nav>',
               "", s, flags=re.S)
    cols = []
    for region, zone, names in REGIONS:
        items = [(slugify(nm), nm) for nm in names if slugify(nm) in RECS]
        lis = "".join('<li><a href="ceramic-coating-%s.html">%s</a></li>' % (sl, esc(nm)) for sl, nm in items)
        cols.append('<nav class="sm-col" aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>' % (esc(region), esc(region), lis))
    block = "<!--SEOCOLS-->" + "".join(cols) + "<!--/SEOCOLS-->"
    s = s.replace('    </div>\n    <p class="sm-note">', "      " + block + '\n    </div>\n    <p class="sm-note">', 1)
    s = s.replace('<a href="#areas">Service Areas</a>', '<a href="service-areas.html">Service Areas</a>')
    open(p, "w", encoding="utf-8").write(s)


# ------------------------------------------------------------------ main
def main():
    if MISSING:
        print("NOTE: no boundary for %d suburb(s), skipped: %s" % (len(MISSING), ", ".join(MISSING)))
    print("Areas nav/drawer/footer link added on %d pages" % ensure_area_links())
    load_chrome()

    for s in RECS:
        open(os.path.join(ROOT, "ceramic-coating-%s.html" % s), "w", encoding="utf-8").write(suburb_page(s))
    print("suburb pages: %d" % len(RECS))

    sx, facts = explorer()
    open(os.path.join(ROOT, "service-areas.html"), "w", encoding="utf-8").write(hub_page(sx, facts))
    print("service-areas.html: hub, %(n)d suburbs, %(zones)d areas, rings to %(radius)d km" % facts)

    ip = os.path.join(ROOT, "index.html")
    idx = open(ip, encoding="utf-8").read()
    blk = home_block(sx, facts)
    if "<!--SAM-START-->" not in idx:
        raise SystemExit("index.html has no SAM markers")
    idx = re.sub(r"<!--SAM-START-->.*?<!--SAM-END-->\s*", lambda m: blk, idx, flags=re.S)
    ld = ("<!--LD-START-->\n<script type=\"application/ld+json\">%s</script>\n<!--LD-END-->\n"
          % json.dumps(home_ld(facts), ensure_ascii=False))
    if "<!--LD-START-->" in idx:
        idx = re.sub(r"<!--LD-START-->.*?<!--LD-END-->\n", lambda m: ld, idx, flags=re.S)
    else:
        idx = idx.replace("</head>", ld + "</head>", 1)
    open(ip, "w", encoding="utf-8").write(idx)
    print("index.html: explorer block %d KB + business schema" % (len(blk) // 1024))

    cp = os.path.join(ROOT, "css", "styles.css")
    css = open(cp, encoding="utf-8").read()
    marker = "\n/* =========================================================================\n   Service areas"
    css = css[:css.index(marker)] + "\n" + map_css()
    open(cp, "w", encoding="utf-8").write(css)
    print("styles.css: explorer block regenerated for %d areas" % len(ZONES))

    sitemap_html()
    print("sitemap.xml: %d urls; sitemap.html columns rebuilt" % sitemap_xml())

    # styles.css just changed, so every page must reference the new version or
    # returning visitors keep a stale copy.
    bumped = 0
    for p in glob.glob(os.path.join(ROOT, "*.html")):
        t = open(p, encoding="utf-8").read()
        t2 = re.sub(r"(css/styles\.css\?v=)\d+", r"\g<1>" + CSSV, t)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2); bumped += 1
    print("styles.css?v=%s on %d more pages" % (CSSV, bumped))


if __name__ == "__main__":
    main()
