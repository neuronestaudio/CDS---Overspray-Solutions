# -*- coding: utf-8 -*-
"""Single source of truth for CDS's service areas.

CDS works out of a studio in Berwick VIC 3806. The service area is every gazetted
suburb within 40 km of it: Casey, Cardinia, Greater Dandenong, Knox, Monash, Kingston,
Frankston, Maroondah, Whitehorse, Manningham, Glen Eira, Bayside, Stonnington,
Boroondara, Port Phillip, the Dandenong Ranges, the Yarra Valley and the Western Port
side of the Mornington Peninsula. radius_census.py measures the rings: 181 suburbs
sit within 30 km of Berwick and 287 within 40 km (OSM admin_level=9, centre to
centre). All 287 are covered except Moorabbin Airport (an airport) and French Island
(no road access), which are deliberately skipped.

Regions group suburbs for the sitemap, breadcrumbs and the service-areas hub.
ZONES groups regions into the filter chips on the homepage map. Archetypes (what
the paint is up against in that *kind* of place) are assigned in assign.py.

Karingal is deliberately absent: OSM holds it only as a point inside Frankston's
boundary, with no polygon of its own, so it would need an invented shape.

Add a suburb here, re-run the pipeline (README.md), and the page, the maps, the
neighbour links and both sitemaps all follow.
"""
import re

STUDIO = ("Berwick", "3806")

REGIONS = [
    ("Berwick & surrounds", "casey", [
        "Berwick", "Beaconsfield", "Narre Warren", "Narre Warren North",
        "Narre Warren South", "Harkaway", "Officer",
    ]),
    ("Hallam, Endeavour Hills & Hampton Park", "casey", [
        "Hallam", "Endeavour Hills", "Doveton", "Eumemmerring", "Hampton Park",
        "Lynbrook", "Lyndhurst", "Lysterfield South",
    ]),
    ("Cranbourne & the southern growth corridor", "south", [
        "Cranbourne", "Cranbourne North", "Cranbourne East", "Cranbourne West",
        "Cranbourne South", "Clyde", "Clyde North", "Botanic Ridge",
        "Junction Village", "Devon Meadows",
    ]),
    ("Western Port", "south", [
        "Pearcedale", "Tooradin", "Blind Bight", "Warneet", "Cannons Creek",
        "Somerville", "Tyabb", "Hastings", "Baxter", "Bittern", "Crib Point",
        "Jam Jerrup",
    ]),
    ("Pakenham & Cardinia", "east", [
        "Pakenham", "Pakenham South", "Officer South", "Cardinia", "Nar Nar Goon",
        "Nar Nar Goon North", "Tynong", "Tynong North", "Garfield", "Garfield North",
        "Bunyip", "Bunyip North", "Koo Wee Rup", "Lang Lang", "Bayles", "Catani",
        "Yannathan", "Iona", "Maryknoll", "Rythdale", "Cora Lynn", "Dalmore",
        "Heath Hill", "Koo Wee Rup North", "Monomeith", "Caldermeade", "Vervale",
        "Tonimbuk", "Lang Lang East",
    ]),
    ("West Gippsland edge", "east", [
        "Longwarry", "Longwarry North", "Labertouche", "Modella",
    ]),
    ("Beaconsfield Upper & the Cardinia hills", "hills", [
        "Beaconsfield Upper", "Guys Hill", "Dewhurst", "Pakenham Upper",
        "Mount Burnett", "Narre Warren East", "Emerald", "Cockatoo", "Gembrook",
        "Avonsleigh", "Clematis", "Menzies Creek", "Macclesfield", "Nangana",
    ]),
    ("Dandenong Ranges", "hills", [
        "Belgrave", "Belgrave Heights", "Belgrave South", "Upwey", "Tecoma", "Selby",
        "Kallista", "Sherbrooke", "Sassafras", "Ferny Creek", "Olinda", "Monbulk",
        "Silvan", "Kalorama", "Mount Dandenong", "The Patch", "Upper Ferntree Gully",
        "Tremont",
    ]),
    ("Dandenong, Noble Park & Keysborough", "north", [
        "Dandenong", "Dandenong North", "Dandenong South", "Noble Park",
        "Noble Park North", "Keysborough", "Springvale", "Springvale South",
        "Bangholme",
    ]),
    ("Rowville, Knox & Ferntree Gully", "north", [
        "Rowville", "Lysterfield", "Scoresby", "Knoxfield", "Ferntree Gully",
        "Boronia", "Wantirna", "Wantirna South", "Bayswater", "The Basin",
        "Bayswater North", "Heathmont", "Kilsyth", "Kilsyth South",
    ]),
    ("Monash", "north", [
        "Mulgrave", "Wheelers Hill", "Glen Waverley", "Mount Waverley", "Clayton",
        "Notting Hill", "Oakleigh", "Oakleigh East", "Oakleigh South", "Huntingdale",
        "Hughesdale", "Chadstone", "Ashwood", "Vermont South", "Burwood East",
    ]),
    ("Kingston & the bayside", "bay", [
        "Dingley Village", "Braeside", "Mordialloc", "Aspendale", "Aspendale Gardens",
        "Edithvale", "Chelsea", "Chelsea Heights", "Bonbeach", "Carrum",
        "Patterson Lakes", "Waterways", "Mentone", "Parkdale", "Cheltenham",
        "Heatherton", "Clayton South", "Clarinda", "Moorabbin",
    ]),
    ("Glen Eira & Bayside", "bay", [
        "Beaumaris", "Black Rock", "Sandringham", "Hampton East", "Highett",
        "Bentleigh East", "Bentleigh", "McKinnon", "Ormond", "Glen Huntly", "Carnegie",
        "Murrumbeena", "Malvern East", "Ashburton",
    ]),
    ("Ringwood, Croydon & Maroondah", "outer", [
        "Montrose", "Croydon South", "Croydon", "Croydon North", "Croydon Hills",
        "Mooroolbark", "Mount Evelyn", "Lilydale", "Ringwood", "Ringwood East",
        "Ringwood North", "Warranwood", "Donvale", "Park Orchards", "Chirnside Park",
    ]),
    ("Box Hill, Nunawading & Whitehorse", "outer", [
        "Vermont", "Forest Hill", "Mitcham", "Nunawading", "Blackburn", "Blackburn South",
        "Blackburn North", "Burwood", "Box Hill", "Box Hill South", "Box Hill North",
    ]),
    ("Doncaster, Templestowe & Warrandyte", "outer", [
        "Doncaster", "Doncaster East", "Templestowe", "Templestowe Lower", "Bulleen",
        "Warrandyte", "Warrandyte South", "Wonga Park",
    ]),
    ("Eltham, Lower Plenty & Ivanhoe East", "outer", [
        "Eltham", "Research", "North Warrandyte", "Bend of Islands", "Lower Plenty",
        "Viewbank", "Ivanhoe East", "Eaglemont",
    ]),
    ("Yarra Valley", "hills", [
        "Wandin East", "Wandin North", "Yellingbo", "Seville", "Hoddles Creek", "Beenak",
        "Seville East", "Woori Yallock", "Launching Place", "Yarra Junction", "Gladysdale",
        "Three Bridges", "Gilderoy", "Gruyere", "Coldstream", "Yering",
    ]),
    ("Toorak, Prahran & St Kilda", "inner", [
        "Toorak", "Armadale", "Malvern", "Kooyong", "Prahran", "Windsor", "South Yarra",
        "St Kilda", "St Kilda East", "St Kilda West", "Balaclava", "Ripponlea", "Elwood",
        "Middle Park",
    ]),
    ("Caulfield, Elsternwick & Brighton", "inner", [
        "Caulfield", "Caulfield North", "Caulfield South", "Caulfield East", "Elsternwick",
        "Gardenvale", "Brighton", "Brighton East", "Hampton",
    ]),
    ("Hawthorn, Kew, Camberwell & Richmond", "inner", [
        "Hawthorn", "Hawthorn East", "Kew", "Kew East", "Camberwell", "Canterbury",
        "Balwyn", "Balwyn North", "Deepdene", "Surrey Hills", "Mont Albert",
        "Mont Albert North", "Glen Iris", "Richmond", "Cremorne", "Burnley", "Abbotsford",
    ]),
    ("Frankston & the peninsula edge", "bay", [
        "Frankston", "Frankston South", "Frankston North", "Seaford",
        "Carrum Downs", "Skye", "Sandhurst", "Langwarrin", "Langwarrin South",
        "Mount Eliza", "Mornington", "Moorooduc", "Mount Martha", "Tuerong",
    ]),
]

ZONES = [
    ("casey", "Berwick & Casey"),
    ("south", "Cranbourne & Western Port"),
    ("east", "Pakenham & Cardinia"),
    ("hills", "The Hills"),
    ("north", "Dandenong, Knox & Monash"),
    ("outer", "Ringwood, Box Hill & Doncaster"),
    ("inner", "Inner South-East"),
    ("bay", "Bayside & Frankston"),
]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def all_targets():
    """[(region, zone, name, slug)] in list order. Fails on a duplicate."""
    out, seen = [], set()
    for region, zone, names in REGIONS:
        for name in names:
            slug = slugify(name)
            if slug in seen:
                raise SystemExit("duplicate suburb in REGIONS: %s" % name)
            seen.add(slug)
            out.append((region, zone, name, slug))
    return out


if __name__ == "__main__":
    t = all_targets()
    print("%d regions, %d suburbs, %d zones" % (len(REGIONS), len(t), len(ZONES)))
    for region, zone, names in REGIONS:
        print("  %-44s %-6s %d" % (region, zone, len(names)))
