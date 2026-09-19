# -*- coding: utf-8 -*-
"""Mobile or studio - the one question every suburb page has to answer.

Andy works BOTH ways (confirmed by Dion, 19 Sep 2026; his Yellow Pages and Facebook
listings are literally "Mobile Car Detailing & Overspray Solutions", Berwick 3806):
mobile at the customer's home or workplace, and from the studio in Berwick. Until
this file existed every page said "everything is done at the Berwick studio",
which was wrong.

The FAQ is pinned on every page, so it is assembled from three rotating parts to
stop it becoming the block that makes same-archetype pages read alike:

    OPEN[hash]  +  CORE[archetype]  +  CLOSE[hash]

OPEN carries the facts ({suburb}, {km}); CORE is what actually decides mobile vs
studio in that *kind* of place; CLOSE is the call to action. Nothing here invents
a policy (no call-out fees, no minimum job, no "coatings are studio-only"): the
only rule stated is the true one - a coating has to cure dry and under cover.
"""

QUESTIONS = [
    "Do you come to {suburb}, or do I bring the car in?",
    "Is CDS mobile in {suburb}?",
    "Can the work be done at my place in {suburb}?",
    "Mobile or studio - which suits a {suburb} car?",
]

# Openers are neutral statements on purpose: the question and the opener are picked
# independently, and "Yes - ..." under "Mobile or studio - which suits?" does not parse.
OPEN = [
    "Andy is mobile as well as studio-based, so the work can be done at your place in "
    "{suburb} or at the Berwick studio, about {km} km away.",
    "CDS is mobile across Melbourne's south-east, {suburb} included, and also runs a studio "
    "in Berwick ({km} km from you) if you would rather drop the car in.",
    "We can come to you in {suburb}, or you can bring the car to the studio in Berwick, "
    "roughly {km} km away - both are on offer.",
    "Andy works mobile in {suburb} and from the Berwick studio, which is about {km} km from "
    "you, so it is your choice.",
]

# km == 0: the studio is in this suburb.
OPEN_HOME = ("The studio is right here in Berwick and Andy is mobile as well, so the work can be "
             "done at your place or ours.")

CORE = {
    "established": "Established homes usually have what a mobile job needs - a garage or carport, "
                   "power and water - so most work here can be done on site while you get on with the day.",
    "prestige":    "A garaged home suits a mobile visit well. For a multi-stage correction, where "
                   "controlled lighting shows every last mark, the studio is the better room to work in.",
    "inner":       "Street parking and shared basements are the catch: a coating has to cure dry and "
                   "under cover, and most body corporates do not allow water or power use in the car "
                   "park. With a private garage, mobile works; without one, the studio is the better answer.",
    "family":      "Most family homes have a garage or carport, which is all a mobile job needs, and "
                   "it saves you juggling a second car for the drop-off.",
    "growth":      "In a new estate the issue is dust from the building sites around you. A mobile job "
                   "is done with the garage door down for that reason; if the garage is still full of "
                   "boxes, the studio is the cleaner option.",
    "industrial":  "Work vehicles and fleets can be done at your workplace or depot so they are not "
                   "off the road for a drop-off; private cars at home or in the studio, whichever is easier.",
    "urban":       "It comes down to parking. With a garage or an undercover space and access to power, "
                   "mobile works well. If the car lives on the street, the studio is the better place "
                   "for a coating to cure.",
    "bayside":     "Near the water it is salt air and the sea breeze that matter: a coating needs to "
                   "cure dry and out of the wind. A closed garage does that; otherwise the studio does.",
    "hills":       "In the hills it is the damp and the tree canopy. A coating cannot cure under "
                   "dripping trees, so a mobile job needs a garage or a good carport - otherwise the "
                   "studio keeps it dry.",
    "acreage":     "Acreage properties usually have the room, the shed and the power a mobile job "
                   "needs, so on-site work suits most of what we do out here.",
    "rural":       "A shed or a closed garage is ideal for a mobile job. Some owners would rather tie "
                   "it in with a trip into town and leave the car at the studio instead.",
    "valley":      "Valley mornings are foggy and the dew is heavy, so a coating has to cure under "
                   "cover. A shed or garage makes a mobile job straightforward; without one, the "
                   "studio is the safer choice.",
}

CLOSE = [
    "Tell us where the car is kept when you book and you will get a straight answer on which suits the job.",
    "Mention your parking set-up when you enquire and Andy will say honestly which way gives the better result.",
    "If you are unsure, send a photo of where the car lives with your enquiry and we will work out the best option.",
    "Either way it is the same person, the same products and the same registered warranty.",
]
