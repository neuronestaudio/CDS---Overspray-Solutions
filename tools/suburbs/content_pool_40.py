# -*- coding: utf-8 -*-
"""Archetype pools added when the service area grew from ~32 km to the full 40 km
ring (19 Sep 2026). The inner south-east and the Yarra Valley floor are different
*kinds* of place from anything in content_pool.py, so they get their own pools
rather than being squeezed into `established`, `urban` or `rural`.

Same shape and placeholders as content_pool.py: 3 intros (page shows 1),
8 conditions (shows 4), 6 FAQs (shows 3); {suburb} and {km}.

These suburbs are 30-40 km from the Berwick studio. Andy is mobile as well as
studio-based, so the mobile-or-studio question is answered on every page by the
pinned FAQ in mode_pool.py, not here. Nothing here promises a product CDS does
not list.
"""

EXTRA = {

# ---------------------------------------------------------------------------
"prestige": {
    "label": "Blue-chip and prestige",
    "intros": [
        "{suburb} has one of the highest concentrations of European and performance cars "
        "in Melbourne, and owners who look at their paint in direct sun. That is the "
        "standard we work to: measured, multi-stage correction, and a coating chosen for "
        "how the finish reads, not just how long it lasts.",

        "Most of what comes to us from {suburb} is a late-model prestige car with "
        "dealer-installed swirl marks. Showroom washes, hand-car-wash queues and a quick "
        "polish before delivery leave fine marring and buffer trails that only show "
        "outside - and they are there on cars with delivery kilometres.",

        "A car from {suburb} is usually garaged, serviced on time and genuinely cared "
        "for, which makes the paint worth doing properly. The work is in the detail: "
        "paint depth readings on every panel, the right approach for a hard German "
        "clear coat or a soft Japanese one, and no shortcuts on the finishing stage.",
    ],
    "conditions": [
        ("Hard German clear coat", "BMW, Mercedes, Audi and Porsche paint is hard. It resists marring well, but it takes more passes and the right compound to correct, which is where a rushed job gives itself away."),
        ("Soft Japanese and EV paint", "Lexus, Mazda and Tesla finishes are the opposite - they correct easily and mark easily, so they are polished gently and benefit most from a hard coating on top."),
        ("Dealer-installed swirls", "A new prestige car is often washed and quick-polished several times before handover. The holograms that leaves are correctable, and it is worth doing before anything is sealed over them."),
        ("Hand car wash marring", "The weekly hand wash at a busy car wash uses the same mitts and towels on every car in the queue. It is the most common source of swirls on otherwise immaculate cars."),
        ("Piano black and gloss trim", "Gloss-black pillars, grilles and interior trim scratch if you look at them. They can be refined and coated along with the paint."),
        ("Matte and satin finishes", "Matte and satin paint cannot be machine-polished - polishing makes it glossy and cannot be undone. Tell us before you book so the car is handled correctly from the first wash."),
        ("Paint protection film", "Many cars here already carry film on the front end. Film and coating work well together, and a coating over the film makes it easier to keep clean."),
        ("Low-kilometre garage cars", "Cars that do few kilometres still oxidise and gather dust marks from covers and wipe-downs. They are ideal candidates for a multi-year system because the paint under them is so good."),
    ],
    "faqs": [
        ("Do you work on high-value and exotic cars?", "Yes. Every car is measured panel by panel before correction, and the approach is set by what the clear coat will safely allow - which matters most on cars where a respray is not an acceptable outcome."),
        ("My new car already has swirl marks. Is that normal?", "Unfortunately, yes. Pre-delivery washing and polishing is usually quick rather than careful. The marks are in the clear coat, not through it, and they correct out fully."),
        ("GYEON or ONYX for a prestige car?", "For a garaged car where clarity in direct sun matters most we generally lean GYEON; for one that is driven daily and parked outside, ONYX 10H graphene for durability. Often either is a good answer and we will say so."),
        ("Can you coat a car that already has paint protection film?", "Yes. The coating goes over the film as well as the paint. It adds chemical resistance the film lacks and makes the whole car easier to wash."),
        ("My car has matte paint. Can you help?", "We can wash and protect it correctly, but matte paint cannot be polished, so scratches cannot be corrected the way they can on gloss. Mention it when you book so there are no surprises."),
        ("Will you tell me if correction is not worth doing?", "Yes. If the clear coat is thin from previous polishing, or the defects are too deep to remove safely, you will hear that before any work starts."),
    ],
},

# ---------------------------------------------------------------------------
"inner": {
    "label": "Inner-city living",
    "intros": [
        "In {suburb} most cars live in a basement stacker or on the street, and almost "
        "nobody has a hose. That changes how a car gets cleaned - automatic washes and "
        "quick wipe-downs replace a proper hand wash - and it shows in the paint as "
        "swirls long before the car is old.",

        "Inner-city paint in {suburb} takes a different kind of wear from the suburbs "
        "further out: parallel-parking scuffs, plane-tree sap, bird droppings baked on "
        "between moves, and a fine metallic dust from tram and train lines that a wash "
        "does not shift.",

        "A lot of {suburb} cars do few kilometres and still look tired, because the "
        "damage here comes from how they are stored and cleaned rather than how far "
        "they go. Nearly all of it is in the top of the clear coat, which means it can "
        "be corrected - and a coating makes the next three years much kinder.",
    ],
    "conditions": [
        ("No hose, no driveway", "Apartment living means the car is cleaned at an automatic wash or not at all. Brush washes are the single biggest cause of swirl marks, and a coating makes the touch-free option actually work."),
        ("Tram and rail dust", "Steel wheels on steel rails shed fine metal dust that settles on nearby cars and corrodes into the clear coat as tiny rust specks. It is dissolved chemically, never scrubbed."),
        ("Street-tree sap and droppings", "Plane trees and elms line most streets here. Sap and bird droppings etch within a hot afternoon, and a street-parked car cannot be moved out from under them."),
        ("Parallel-parking scuffs", "Bumper corners and wheel arches collect paint transfer from tight parks. Transfer sits on top of the paint and usually polishes off; kerbed wheels are a separate repair."),
        ("Car stackers and tight ramps", "Basement stackers and narrow ramps leave scrapes along sills and mirrors. We correct what the clear coat allows and are straight about what needs a panel shop."),
        ("Construction overspray", "There is nearly always a building going up nearby. Concrete dust and paint mist from a site drift over parked cars and bond to the paint - removing it is where this business started."),
        ("Permit parking, all weather", "A car that lives on the street takes UV all summer and stays damp all winter. Sealed paint is what stops that turning into faded, flat colour."),
        ("Short trips and brake dust", "Stop-start inner-city driving loads the front wheels with hot brake dust that bakes into the finish. Coated wheels release it with a rinse."),
    ],
    "faqs": [
        ("I can only use automatic car washes. Is a coating still worth it?", "More so. Use a touch-free wash rather than a brush wash. On coated paint the dirt is not bonded, so a touch-free wash actually gets the car clean, and the swirls stop accumulating."),
        ("Can you remove the little rust-coloured specks on my paint?", "Yes. That is rail or brake dust embedded in the clear coat. It is dissolved with an iron treatment and clayed out, then the paint is sealed so it has a much harder time coming back."),
        ("Can you get paint transfer and scuffs off my bumper?", "Usually. Transfer from another car or a bollard sits on the surface and polishes off. If the scratch is through the clear coat we will tell you before quoting."),
        ("My car lives under a street tree. What helps most?", "A coating. It will not stop sap and droppings landing, but it stops them bonding, so they can be lifted off safely instead of leaving an etched ring."),
        ("There is a building site next to where I park. Can overspray be removed?", "Yes - it is our specialty. Concrete spatter and paint mist are removed without cutting into the clear coat, and we can provide a written assessment if you are claiming against the builder."),
        ("Do you coat wheels and glass too?", "Yes. Coated wheels stop brake dust baking on, and coated glass sheds rain and cuts glare, which helps most in inner-city night driving."),
    ],
},

# ---------------------------------------------------------------------------
"valley": {
    "label": "The Yarra Valley",
    "intros": [
        "{suburb} is valley country - vineyards, orchards, gravel side roads and a long "
        "highway run to anywhere. Cars here pick up fine dust in summer, mud in winter "
        "and a steady diet of bugs and road film in between.",

        "Living in {suburb} means a car that works across very different surfaces in a "
        "single week: sealed highway, gravel driveways, wet paddock edges and the odd "
        "cellar-door car park. Most of what that does to paint is abrasive, and abrasive "
        "damage is exactly what a sealed surface resists best.",

        "The Yarra Valley is hard on a finish in quiet ways. Around {suburb} it is "
        "morning fog that keeps a car wet for hours, dust that settles on the damp, and "
        "sap from the gums along the road. A coating is what stops that mix keying into "
        "the clear coat.",
    ],
    "conditions": [
        ("Gravel-road dust", "Unsealed side roads put a fine, abrasive film over the whole car. It has to be rinsed off, not wiped - wiping it dry is what scratches valley cars."),
        ("Vineyard and orchard spray drift", "Agricultural sprays can drift onto cars parked near vines and orchards and dry as a spotted residue on paint and glass. On sealed paint it rinses off far more easily."),
        ("Fog, frost and long damp mornings", "Valley fog keeps panels wet well into the morning, which gives dust, sap and droppings longer to work on the paint."),
        ("Bug strike on the highway run", "Long highway drives at dusk coat the front of the car in insects. The residue is acidic and etches if it is left; coated paint releases it with a gentle wash."),
        ("Winter mud and clay", "Wet-season mud packs into wheel arches and sills and holds moisture against the metal. It releases far more easily from coated surfaces."),
        ("Roadside gum sap", "Eucalypts along the valley roads drop sticky, acidic sap that sets hard in the sun and etches a ring into unprotected clear coat."),
        ("Utes, floats and trailers", "Working utes and tow vehicles cop mud, feed and gravel rash. Coating the tray, canopy and paint makes the hose-down quick."),
        ("Stone chips from loose surfaces", "Gravel flicks up into the bonnet and sills. A coating does not stop chips, but it seals the paint around them so they are less of a way in for corrosion."),
    ],
    "faqs": [
        ("Will a coating really help with the dust?", "Yes. Dust does not bond to sealed paint, so a rinse lifts it instead of a wipe, and that is what prevents the scratching."),
        ("Can spray-drift marks be removed?", "Usually. Fresh residue washes off; older spotting that has etched can normally be polished out. Coating afterwards makes the next lot much easier to deal with."),
        ("Do you coat utes and 4WDs?", "Yes - paint, trays, canopies, bars and trim. A coated working vehicle takes a fraction of the time to clean."),
        ("How do I get bug marks off the front?", "Soak them rather than scrub them, and do it soon after the drive. On coated paint they barely stick; etched marks can usually be polished out."),
        ("Will a coating stop stone chips?", "No. Chips are impact damage and only paint protection film reduces them. A coating protects the surrounding paint and makes the car easier to keep clean."),
        ("How should I wash a car that is always dusty?", "Rinse thoroughly first so the grit floats off, then wash with a proper car shampoo. Never wipe dust off a dry panel."),
    ],
},
}
