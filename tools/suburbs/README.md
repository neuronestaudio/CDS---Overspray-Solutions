# Suburb page pipeline

Generates the 209 `ceramic-coating-<suburb>.html` pages, the `service-areas.html`
hub, the interactive map block on the homepage, and both sitemaps. Ported from the
Ronin build (itself JED -> East Shore). Every network step caches, so re-running is
cheap and only fills in what is missing.

```
python suburb_list.py        # sanity check: regions, suburbs, zones
python assign.py             # every suburb in exactly one archetype
python fetch_boundaries.py   # Nominatim -> boundaries.json (1 req/sec, + postcode pass)
python fetch_landmarks.py    # Overpass -> landmarks.json (cached payloads)
python emit_pages.py         # pages, hub, homepage map, sitemaps, styles.css version
python ../verify_area_similarity.py   # ALWAYS - fails above 0.72
python radius_census.py      # optional: how many suburbs within 30 / 40 km of Berwick
```

`suburb_list.py` is the single source of truth. Add a suburb there, give it an
archetype in `assign.py`, re-run, and the page, both maps, the neighbour links and
the sitemaps all follow. Pages emit the live host, https://cardetailingsolutions.com.au.
If a suburb is ever removed, add a 308 for its URL to `vercel.json` (append to the
existing `redirects` array - it also holds the old site's `.php` redirects).

## Why the content is structured this way

209 pages off one template is the doorway-page pattern Google filters. So the
substance lives in 9 **archetypes** (`content_pool.py`: new estates, established,
family, industrial, urban, bayside, hills, acreage, rural), each with a pool bigger
than a page renders (3 intros / 8 conditions / 7 FAQs; a page shows 1 / 4 / 3).
`shared_pool.py` rotates the blocks that would otherwise be identical everywhere
(lede, owner paragraph, headings, process strip, CTA). Each page picks by an FNV-1a
hash of its own slug. Localised with facts that are that place's own: postcode,
land area, distance to the studio, true polygon neighbours, real named landmarks.

Last measurement (19 Sep 2026): 209 pages, 2,649 same-archetype pairs, mean 0.174,
worst 0.570, threshold 0.72. Largest archetype is `family` (43 pages) - widen its
pool first if a future expansion pushes it over.

## Things that will bite you

- **Victorian suburbs are `admin_level=9` in OSM, not 10.** A query for 10 returns
  nothing at all rather than an error.
- **The bounding box silently rejects.** At a north edge of -37.82, Kilsyth (centre
  -37.819) came back NO MATCH, not as an error. The box now runs to -37.68 to clear
  Lilydale. Widen it before adding anything further out.
- **Karingal has no boundary of its own in OSM** - only a point inside Frankston's
  polygon. It was dropped rather than given an invented shape.
- **Koo Wee Rup North has no postcode** in OSM; the page omits it rather than guess.
- **Overpass 504s** on a box this size. Both Overpass scripts fall back to two
  mirrors; the parks query sometimes needs a second run.
- **Landmark dedupe:** `norm()` strips only parentheticals and "shopping
  centre/village". Stripping "station" or "plaza" made Clayton station and Clayton
  Plaza collide and the station vanished. A name that extends an already-picked
  one ("Box Hill Central South") is treated as the same place.
- `DROP` in `fetch_landmarks.py` was built by reading the full output: depots, gas
  terminals, freeway service centres, coded reserves ("G76"), HomeCo repeats. Read
  the output again after widening the box - new junk arrives with new suburbs.
