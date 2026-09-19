# -*- coding: utf-8 -*-
"""Suburb -> archetype.

An archetype is what a car's paint is actually up against in that *kind* of
place: salt on the bay, gum sap and damp in the Ranges, render and paint mist
beside a new estate, fallout next to an industrial belt. The content pools in
content_pool.py are written per archetype, not per suburb.

Every suburb in suburb_list.py must appear exactly once below; run this file to
check.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from suburb_list import all_targets

ARCH = {
    # leafy, established, a lot of garaged and prestige cars
    "established": [
        "Berwick", "Beaconsfield", "Narre Warren North", "Wheelers Hill", "Glen Waverley",
        "Mount Waverley", "Vermont South", "Burwood East", "Ashwood", "Mount Eliza",
        "Frankston South", "Heathmont", "Dingley Village", "Rowville", "Mulgrave",
        "Montrose", "Warranwood", "Donvale", "Ringwood North", "Blackburn",
        "Blackburn North", "Malvern East", "Ashburton",
        "Box Hill North", "Doncaster", "Doncaster East", "Templestowe", "Templestowe Lower",
        "Bulleen", "Lower Plenty", "Viewbank",
    ],
    # blue-chip inner east and bayside: European marques, hard and soft clear coats,
    # owners who look at the paint in direct sun
    "prestige": [
        "Toorak", "Armadale", "Malvern", "Kooyong", "Glen Iris", "Camberwell", "Canterbury",
        "Surrey Hills", "Mont Albert", "Mont Albert North", "Balwyn", "Balwyn North",
        "Deepdene", "Kew", "Kew East", "Hawthorn East", "Brighton East", "Caulfield",
        "Caulfield North", "Caulfield South", "Gardenvale", "Ivanhoe East", "Eaglemont",
    ],
    # inner city: apartments, basement stackers, tram streets, no hose
    "inner": [
        "St Kilda", "St Kilda East", "St Kilda West", "Balaclava", "Ripponlea", "Elwood",
        "Elsternwick", "Windsor", "Prahran", "South Yarra", "Richmond", "Cremorne",
        "Burnley", "Abbotsford", "Middle Park", "Hawthorn",
    ],
    # Yarra Valley floor: vineyards, orchards, gravel, fog, long highway runs
    "valley": [
        "Seville East", "Woori Yallock", "Launching Place", "Yarra Junction", "Gladysdale",
        "Three Bridges", "Gilderoy", "Gruyere", "Coldstream", "Yering",
    ],
    # 1970s-90s family suburbs, long-owned cars, a lot of wash marring
    "family": [
        "Narre Warren", "Hampton Park", "Endeavour Hills", "Doveton", "Eumemmerring",
        "Cranbourne", "Ferntree Gully", "Boronia", "Bayswater", "Bayswater North",
        "Knoxfield", "Wantirna", "Wantirna South", "Kilsyth", "Noble Park North",
        "Dandenong North", "Frankston North", "Langwarrin", "Oakleigh East",
        "Oakleigh South", "Clarinda", "Notting Hill", "Chelsea Heights",
        "Croydon", "Croydon South", "Croydon North", "Croydon Hills", "Mooroolbark",
        "Lilydale", "Ringwood East", "Vermont", "Forest Hill", "Mitcham", "Nunawading",
        "Blackburn South", "Burwood", "Box Hill South", "Highett", "Bentleigh East",
        "Bentleigh", "McKinnon", "Ormond", "Murrumbeena", "Chirnside Park",
    ],
    # new estates: brand-new cars parked beside active building sites
    "growth": [
        "Clyde", "Clyde North", "Officer", "Officer South", "Cranbourne North",
        "Cranbourne East", "Cranbourne West", "Botanic Ridge", "Lynbrook",
        "Narre Warren South", "Pakenham", "Pakenham South", "Junction Village",
        "Waterways", "Skye", "Sandhurst", "Aspendale Gardens",
    ],
    # beside an industrial belt: fallout, overspray, heavy vehicles
    "industrial": [
        "Dandenong South", "Lyndhurst", "Bangholme", "Braeside", "Keysborough",
        "Springvale South", "Clayton South", "Heatherton", "Moorabbin",
        "Kilsyth South", "Hallam", "Carrum Downs", "Scoresby",
    ],
    # busy, dense, kerbside parking and heavy traffic
    "urban": [
        "Dandenong", "Noble Park", "Springvale", "Clayton", "Oakleigh", "Huntingdale",
        "Hughesdale", "Chadstone", "Frankston", "Cheltenham", "Mentone",
        "Ringwood", "Box Hill", "Carnegie", "Glen Huntly", "Caulfield East",
    ],
    # on the water: salt air, sand, marina and boat-ramp traffic
    "bayside": [
        "Mordialloc", "Aspendale", "Edithvale", "Chelsea", "Bonbeach", "Carrum",
        "Patterson Lakes", "Parkdale", "Seaford", "Mornington", "Mount Martha",
        "Tooradin", "Blind Bight", "Warneet", "Cannons Creek", "Hastings", "Crib Point",
        "Beaumaris", "Black Rock", "Sandringham", "Hampton East", "Hampton", "Brighton",
        "Jam Jerrup",
    ],
    # the Dandenong Ranges and Cardinia hills: shade, damp, sap, leaf litter
    "hills": [
        "Belgrave", "Belgrave Heights", "Belgrave South", "Upwey", "Tecoma", "Selby",
        "Kallista", "Sherbrooke", "Sassafras", "Ferny Creek", "Olinda", "Monbulk",
        "Silvan", "Kalorama", "Mount Dandenong", "The Patch", "Upper Ferntree Gully",
        "The Basin", "Menzies Creek", "Emerald", "Avonsleigh", "Clematis", "Cockatoo",
        "Gembrook", "Macclesfield", "Tremont", "Nangana", "Mount Evelyn",
        "Hoddles Creek", "Beenak", "Warrandyte", "North Warrandyte", "Eltham", "Research",
    ],
    # lifestyle acreage: gravel drives, dust, sheds, utes and floats
    "acreage": [
        "Harkaway", "Guys Hill", "Beaconsfield Upper", "Dewhurst", "Pakenham Upper",
        "Mount Burnett", "Narre Warren East", "Lysterfield", "Lysterfield South",
        "Devon Meadows", "Cranbourne South", "Pearcedale", "Langwarrin South", "Baxter",
        "Moorooduc", "Somerville", "Tyabb", "Tynong North", "Nar Nar Goon North",
        "Garfield North", "Bunyip North", "Bittern", "Park Orchards", "Tonimbuk",
        "Warrandyte South", "Wonga Park", "Tuerong", "Bend of Islands", "Labertouche",
    ],
    # farming flats and country towns: farm roads, mud, long kilometres
    "rural": [
        "Koo Wee Rup", "Lang Lang", "Bayles", "Catani", "Yannathan", "Iona",
        "Maryknoll", "Rythdale", "Cora Lynn", "Dalmore", "Heath Hill", "Cardinia",
        "Nar Nar Goon", "Tynong", "Garfield", "Bunyip", "Koo Wee Rup North", "Monomeith",
        "Caldermeade", "Vervale", "Wandin East", "Wandin North", "Yellingbo", "Seville",
        "Modella", "Lang Lang East", "Longwarry", "Longwarry North",
    ],
}

_BY_NAME = {n: a for a, names in ARCH.items() for n in names}


def archetype_for(name):
    return _BY_NAME[name]


if __name__ == "__main__":
    names = [n for _r, _z, n, _s in all_targets()]
    missing = [n for n in names if n not in _BY_NAME]
    extra = [n for n in _BY_NAME if n not in names]
    dupes = [n for a, ns in ARCH.items() for n in ns
             if sum(n in ns2 for ns2 in ARCH.values()) > 1]
    for a, ns in ARCH.items():
        print("  %-12s %d" % (a, len(ns)))
    print("missing:", missing or "none")
    print("not in list:", extra or "none")
    print("in two archetypes:", sorted(set(dupes)) or "none")
    if missing or extra or dupes:
        raise SystemExit(1)
    print("OK: %d suburbs, %d archetypes" % (len(names), len(ARCH)))
