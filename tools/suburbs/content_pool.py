# -*- coding: utf-8 -*-
"""Content pools for the suburb pages.

~160 pages from one template is the doorway-page pattern. The defence (East Shore,
Ronin) is to put the substance in ARCHETYPES - what a car's paint is up against in
that *kind* of place - give each archetype a pool bigger than any one page renders,
and pick each page's set from a hash of its own slug. Stable across builds,
different between neighbours. tools/verify_area_similarity.py measures it.

Pools per archetype: 3 intros (page shows 1), 8 conditions (shows 4),
7 FAQs (shows 3). Placeholders: {suburb}, {km} (straight-line km to the studio).

Everything here is about CDS as it actually works: an owner-operated studio in
Berwick, GYEON and ONYX coating systems, paint correction, and overspray and
industrial-fallout removal (the specialty the business was built on).
"""

ARCHETYPES = {

# ---------------------------------------------------------------------------
"established": {
    "label": "Established and leafy",
    "intros": [
        "{suburb} is established, well-treed and home to a lot of cars that are garaged "
        "at night and genuinely looked after. That is the best starting point paint can "
        "have: there is real depth in the clear coat to bring back, rather than damage "
        "to disguise.",

        "A lot of what comes to the studio from {suburb} is good paint that has simply "
        "been washed the wrong way for a few years. Garaged, well kept, never neglected "
        "- and still covered in the fine circular marring a mitt and a hurried towel "
        "leave behind. That is exactly what measured correction is for.",

        "Owners in {suburb} tend to notice the difference between a quick polish and a "
        "proper job, which suits the way we work. Every car is measured before it is "
        "touched, corrected in stages rather than one aggressive hit, and sealed with a "
        "coating chosen for clarity as much as durability.",
    ],
    "conditions": [
        ("Swirls on good paint", "The most common issue here is not neglect but wash marring on otherwise sound paint. It is fully correctable, and the result on a dark metallic is dramatic."),
        ("Mature street trees", "Established gardens and nature strips mean sap, blossom and bird droppings, all of which etch into clear coat if they bake on through a warm week."),
        ("Prestige paint systems", "European clear coats are hard and take more passes to correct properly; Japanese and some EV finishes are soft and easy to over-polish. Each gets its own approach."),
        ("Hologramming from past polishing", "A fast rotary polish leaves buffer trails that only show in direct sun. We see plenty of cars that have been 'detailed' this way and need it undone before they can be coated."),
        ("Garage dust and cover marks", "Even garaged cars pick up fine dust, and car covers dragged across a dusty panel leave their own marring. A coating makes the surface far more forgiving of both."),
        ("Weekend cars", "Cars that only come out on good days still oxidise sitting still, and they are usually the ones owners most want kept perfect. They are ideal candidates for a multi-year system."),
        ("Driveway washing in the sun", "Washing on a hot driveway leaves mineral spots that etch as they dry. A coated car sheds water quickly enough that it stops being a problem."),
        ("Resale on a quality car", "On a well-optioned car the paint is one of the first things a buyer judges. Protecting it early is cheaper than correcting it before sale."),
    ],
    "faqs": [
        ("My car is garaged. Is a coating still worth it?", "Yes - garaged cars have the best paint to protect. A coating keeps that finish from picking up wash marring and makes the car far easier to keep perfect between the days it comes out."),
        ("Can you correct paint that has been badly polished before?", "Usually. We measure the clear coat first, because a previous heavy polish may have taken some of it. If there is enough left, holograms and buffer trails can be refined out; if there is not, we will tell you before starting."),
        ("GYEON or ONYX for a prestige car?", "For a garaged car where the look in direct sun matters most we generally lean GYEON for its clarity; for a car that does real kilometres, ONYX 10H graphene for durability. Often either is a good answer and we will say so."),
        ("How far is the studio from {suburb}?", "About {km} km. Everything is done at the Berwick studio because a coating has to cure in a clean, controlled space to reach its rated life."),
        ("Will a coating change how my paint looks?", "It sharpens it. A properly corrected and coated finish reads deeper and glossier, and it stops the flat, hazy look paint gets as it oxidises."),
        ("Do you work on classic and collector cars?", "Yes. Older single-stage and early clear-coat paint needs a gentler approach and more care than a modern finish, which is exactly how we treat it."),
        ("What maintenance does a coated car need?", "A proper hand wash with a pH-neutral shampoo, and a check-over once a year. Avoid automatic brush washes - they are the fastest way to wear any coating down."),
    ],
},

# ---------------------------------------------------------------------------
"family": {
    "label": "Established family suburbs",
    "intros": [
        "{suburb} is established family country - the kind of suburb where a car does "
        "school runs, weekend sport and the supermarket, often for a decade. That is "
        "hard, honest wear, and most of it is surface damage that correction can take "
        "back out.",

        "Cars in {suburb} work for a living. They get washed quickly between everything "
        "else, parked on the street when the driveway is full, and loaded with kids, "
        "dogs and sports gear. The paint shows all of that - and nearly all of it is "
        "fixable.",

        "Most cars we see from {suburb} have sound original paint under years of light "
        "marring, bird-dropping etching and a bit of fade on the roof and bonnet. That "
        "combination responds very well to a proper cut and polish, and a coating stops "
        "it coming straight back.",
    ],
    "conditions": [
        ("Quick-wash swirls", "Fast washes with one bucket and whatever towel is closest put circular marring into the paint that only shows in the sun. It is the single most common thing we correct."),
        ("Second and third cars outside", "When the garage holds one car, the rest live on the driveway or the street, taking full sun and whatever falls from the trees."),
        ("Bird droppings on the school run", "Droppings are acidic and etch into hot paint within an afternoon. Coated paint gives you the time to wipe them off safely."),
        ("Fading on the horizontal panels", "Roofs, bonnets and boot lids take the most sun. On reds and dark colours that shows up as a flat, chalky finish that a wash no longer shifts."),
        ("Interior wear from family life", "Food, drinks, muddy boots and dog hair. Interior coatings seal fabric and leather so spills can be blotted up instead of soaking in."),
        ("Door dings and car park marks", "Shopping-centre car parks leave light scuffs and transfer on door edges. Transfer can usually be polished off; a coating makes the next one easier to remove."),
        ("Brake dust on busy wheels", "Stop-start suburban driving loads wheels with hot brake dust that bakes into the finish. Coated wheels rinse clean instead."),
        ("Keeping a long-term car presentable", "If the plan is to keep the car for years, protecting it once properly costs less than repeated polishing that thins the clear coat each time."),
    ],
    "faqs": [
        ("Is a coating worth it on a family car?", "Often more than on a show car. A family car gets washed quickly and often, and a coating makes those washes far less damaging while keeping mess from sticking."),
        ("Can you get rid of the swirl marks?", "Yes - swirls are fine scratches in the clear coat, and machine correction levels them out. The coating afterwards is what stops them coming straight back."),
        ("Can you do the inside as well?", "Yes. We deep-clean and coat leather, fabric and trim so spills, dye transfer and grime stop soaking in."),
        ("How long will I be without the car?", "Most coatings are a one to three day job depending on how much correction the paint needs. You will get an exact timeframe when we assess it."),
        ("How far is the studio from {suburb}?", "About {km} km - the studio is in Berwick. Coatings are done there rather than on a driveway because they need a clean, controlled space to cure properly."),
        ("My roof has gone chalky. Can that be fixed?", "If the clear coat is oxidised but still intact, a restoration polish usually brings the colour back. If it has started to peel, no polish will fix it and we will tell you straight."),
        ("Do I need to change how I wash the car?", "Just avoid automatic brush washes and use a proper car shampoo. The coating makes everything else easier."),
    ],
},

# ---------------------------------------------------------------------------
"growth": {
    "label": "New estates and growth corridors",
    "intros": [
        "{suburb} is still being built around the people living in it, and that is a "
        "particular risk for a new car. Render spatter, paint mist from the house next "
        "door and fine cutting dust drift a long way on a windy day, and they bond to "
        "fresh clear coat rather than washing off.",

        "Most of the cars we see from {suburb} are only a year or two old, parked in a "
        "street where half the lots are still building sites. That is the ideal time to "
        "protect paint - and the most common time for it to pick up construction "
        "overspray.",

        "A new estate like {suburb} is exactly the situation CDS was built for. "
        "Overspray and construction fallout removal is where the business started, and "
        "new cars parked beside active sites are the single biggest source of it we "
        "deal with.",
    ],
    "conditions": [
        ("Construction overspray", "Paint mist from a house being finished next door drifts across the street and settles as a rough film. Washing does nothing; it has to be lifted off without cutting into the clear coat."),
        ("Render and concrete spatter", "Tiny grey dots across a bonnet or windscreen are usually render or concrete slurry. Left alone they etch; caught early they come off cleanly."),
        ("Cutting and site dust", "Brick and tile cutting throws up fine abrasive dust that settles on every car in the street. Wiping it off dry is how new paint gets scratched."),
        ("New cars, unprotected", "A new car's paint is the best it will ever be on delivery day. Sealing it before the first wash mark goes in is the cheapest protection there is."),
        ("Young trees, full sun", "New streets have little shade, so cars sit in unbroken sun most of the day. UV is what turns dark paint flat over a few summers."),
        ("Mud on unfinished roads", "Temporary roads and unsealed lots mean mud and clay thrown up the sills and wheel arches, which bakes on if it is left."),
        ("Dealer protection packages", "Many new cars from the area arrive with a dealer 'protection' spray that lasts months, not years. A professionally applied coating is a different product."),
        ("Industrial fallout from transport", "New cars often arrive with rail and transport fallout already bonded to the paint from shipping. It is removed before anything is sealed over it."),
    ],
    "faqs": [
        ("There is building work in my street. Can you remove overspray?", "Yes - it is our specialty. Overspray, render and concrete spatter are removed non-abrasively so the clear coat is preserved, then the paint is coated so the next round of site dust washes off."),
        ("Should I coat a brand-new car?", "It is the best time to. The paint is undamaged, so there is little or nothing to correct and the coating bonds to a perfect surface."),
        ("Is the dealer's paint protection enough?", "Usually not. Dealer packages are typically a quick spray sealant that lasts months. A certified GYEON or ONYX coating is a different class of product and lasts years."),
        ("How far is the studio from {suburb}?", "About {km} km, in Berwick. The car needs to come in because coatings have to cure in a clean, dust-free space - which a street full of building sites is not."),
        ("Can overspray be removed without a respray?", "In the large majority of cases, yes. It sits on top of the clear coat and can be lifted off, provided it has not been left long enough to etch deeply."),
        ("How soon should I deal with overspray?", "As soon as you notice it. Fresh overspray lifts far more easily than overspray that has baked on through a hot week."),
        ("Can you do the glass and wheels too?", "Yes. Glass picks up just as much site dust as paint, and coated wheels stop brake dust and mud baking on."),
    ],
},

# ---------------------------------------------------------------------------
"industrial": {
    "label": "Beside an industrial belt",
    "intros": [
        "{suburb} sits beside working industry, and that changes what settles on a car "
        "here. Fine airborne metal, paint overspray from nearby workshops and grit from "
        "heavy vehicles land on horizontal panels and bond to the clear coat.",

        "If your paint in {suburb} still feels rough straight after a wash, that is "
        "bonded industrial fallout - tiny metal particles corroding into the clear "
        "coat. It needs dissolving out chemically, not scrubbing, which is core CDS "
        "work.",

        "Cars parked or garaged near the industrial estates around {suburb} collect "
        "contamination most suburban cars never see. The good news is that almost all "
        "of it is removable, and once the paint is properly clean a coating stops it "
        "keying in again.",
    ],
    "conditions": [
        ("Industrial fallout", "Airborne metal particle lands on the bonnet, roof and boot and corrodes into the clear coat as tiny orange specks. It is dissolved with an iron treatment, then clayed out."),
        ("Workshop overspray", "Spray booths and fabrication shops release paint mist that drifts onto cars in nearby car parks. It bonds hard and is removed without cutting the paint down."),
        ("Heavy-vehicle grime", "Trucks and machinery leave an oily diesel film on everything around them. It makes a car look dirty two days after a wash because it re-sticks to bare paint."),
        ("Work utes and vans", "Vehicles that work on site take dust, spatter and chemical splashes. Coating them makes the end-of-day clean far quicker."),
        ("Rough paint on a clean car", "The plastic-bag test tells you: run your hand over a washed panel inside a thin bag. If it feels like fine sandpaper, the paint is contaminated."),
        ("Rail dust", "Rail lines shed fine metal dust that behaves exactly like industrial fallout and needs the same chemical removal."),
        ("Brake and road grit", "Industrial roads carry a lot of grit and brake dust, which loads wheels and lower panels faster than a normal suburban street."),
        ("Parking at work all day", "Cars left in an industrial car park all day take the full dose. A coating is what stops the contamination bonding while you are at work."),
    ],
    "faqs": [
        ("Why does my paint feel rough after a wash?", "That is almost always bonded industrial fallout or overspray. A wash slides over it; it has to be removed chemically and with a clay treatment."),
        ("Can you remove overspray from a work car park?", "Yes - it is where the business started. We lift it off non-abrasively so the clear coat is preserved, and can provide a written assessment if you are claiming against the source."),
        ("Do you coat work utes and vans?", "Yes, including trays, canopies and trim. A coated work vehicle takes a fraction of the time to clean."),
        ("How far is the studio from {suburb}?", "About {km} km - we are in Berwick. Decontamination and coating are done in the studio so the paint is sealed clean, not over whatever is in the air outside."),
        ("Will fallout come back after it is removed?", "The environment will keep putting it there, but on coated paint it struggles to bond and most of it comes off in a normal wash."),
        ("Is fallout the same as overspray?", "No. Fallout is metal particle that corrodes into the clear coat; overspray is paint or similar material that bonds on top. They are removed differently, which is why we assess before touching the paint."),
        ("Can fallout damage be permanent?", "If it is left long enough to pit the clear coat, some marks may need correction and a few can be too deep to remove fully. Caught early, it comes out cleanly."),
    ],
},

# ---------------------------------------------------------------------------
"urban": {
    "label": "Busy, dense and kerbside",
    "intros": [
        "{suburb} is busy - heavy traffic, dense streets and a lot of cars that live at "
        "the kerb rather than in a garage. That means constant road film, tight parking "
        "and paint that rarely gets a break.",

        "Cars in {suburb} deal with the pace of a busy centre: stop-start traffic, "
        "crowded car parks and street parking where every passing car and bike brushes "
        "a little closer than it should. Most of what that does to paint is surface "
        "damage, and surface damage can be corrected.",

        "Kerbside parking and heavy traffic around {suburb} put a very particular load "
        "on a car: an oily traffic film that bonds to bare clear coat, brake dust, and "
        "a steady stream of light scuffs. A coating is what makes all of it manageable.",
    ],
    "conditions": [
        ("Traffic film", "Exhaust and brake residue from heavy traffic forms an oily film that bonds to unprotected paint and makes a car look grubby within days of a wash."),
        ("Kerbside scuffs", "Street parking means brushed flanks, transfer on bumper corners and door-edge chips. Transfer usually polishes off; a coating makes the next one easier."),
        ("Crowded car parks", "Tight bays at busy centres mean door dings and scrapes. We correct what the clear coat allows and are straight about what needs a panel shop."),
        ("Brake dust", "Stop-start driving loads wheels with hot brake dust that bakes into the finish. Coated wheels release it with a rinse."),
        ("No off-street parking", "Without a garage there is no shelter from sun, sap or droppings. That is precisely when a sealed surface earns its keep."),
        ("Wash-and-go marring", "Busy people wash quickly. Quick washing is what puts swirl marks into paint, and it is fully correctable."),
        ("Bird droppings in town", "Pigeons and street trees mean frequent direct hits. Acidic droppings etch fast in summer; coated paint lets them wipe off."),
        ("Interior grime from daily use", "Commuting, takeaway and passengers wear interiors quickly. Interior coatings keep fabric and leather from soaking up spills."),
    ],
    "faqs": [
        ("I park on the street. Is a coating worth it?", "That is when it is most worth it. Kerbside paint has no shelter, and a coating stops sun, droppings and traffic film from getting into the clear coat."),
        ("Can you remove scuffs and paint transfer?", "Usually. Transfer from another car or a pole sits on top of the paint and polishes off. If a scratch is through the clear coat we will tell you before quoting."),
        ("How far is the studio from {suburb}?", "About {km} km, in Berwick. Coatings are applied and cured there, in a controlled space."),
        ("Will a coating stop door dings?", "No - nothing liquid stops an impact. It resists wash marring, etching and grime; for impact protection on high-risk areas, paint protection film is the right product."),
        ("Why does my car look dirty so soon after a wash?", "That is traffic film re-bonding to bare paint. On coated paint it cannot key in the same way, so the car stays cleaner for longer."),
        ("Do you do wheels and glass as well?", "Yes. Coated wheels stop brake dust baking on, and coated glass sheds rain at speed and cuts night glare."),
        ("Can you work around my schedule?", "The studio is open seven days by appointment, and we will give you a realistic drop-off and pick-up window when you book."),
    ],
},

# ---------------------------------------------------------------------------
"bayside": {
    "label": "Bayside and coastal",
    "intros": [
        "Salt is the whole story in {suburb}. Air off the water carries a fine saline "
        "film that settles on paint, trim and brightwork and keeps working on it long "
        "after the car looks dry.",

        "Living by the water in {suburb} is hard on a car in ways that are easy to miss. "
        "Salt spray settles on every surface, the sun off the water is relentless, and "
        "sand finds its way into sills, wheel arches and carpet regardless of how "
        "careful anyone is.",

        "Coastal paint ages faster than paint twenty minutes inland, and {suburb} is no "
        "exception. Salt accelerates corrosion around chips and trim, and UV reflected "
        "off the water flattens colour. Sealing the surface is the single most useful "
        "thing you can do.",
    ],
    "conditions": [
        ("Salt air", "A fine saline film settles on the car constantly and attracts moisture. On a coated car it rinses off; on bare paint it sits and works away at it."),
        ("Sand in everything", "Sand is abrasive. Wiping it off a panel scratches the paint, and it packs into sills, seat rails and carpet."),
        ("Reflected UV", "Sun off the water adds to the direct UV load, which is what fades reds and blacks and chalks plastic trim."),
        ("Corrosion around chips", "Salt gets into stone chips and door-edge damage and starts corrosion faster than it would inland. Sealing the surrounding paint slows it down."),
        ("Boat ramp and marina runs", "Towing through salt water and parking near the ramp puts salt straight onto the lower panels and wheels. They need a proper rinse, and coating makes that rinse effective."),
        ("Chrome and brightwork", "Exterior metal trim pits and dulls in salt air. Coating it keeps it bright."),
        ("Beach-day interiors", "Wet towels, sunscreen and sand wear interiors quickly. Coated fabric and leather resist sunscreen marks and moisture."),
        ("Windscreen haze", "Salt film on glass scatters light and makes night driving harder. Glass coating keeps it clearer and sheds water at speed."),
    ],
    "faqs": [
        ("Does salt air really damage paint?", "Yes. Salt holds moisture against the surface and accelerates corrosion wherever the paint is chipped. A coating stops the film bonding and lets it rinse away."),
        ("How often should I wash a car near the water?", "More often than inland - a thorough rinse after windy days and beach trips helps a lot. On a coated car that rinse does most of the work."),
        ("Can you coat the chrome and trim?", "Yes. Brightwork and plastic trim suffer as much as paint by the water, and both can be coated."),
        ("How far is the studio from {suburb}?", "About {km} km. Coatings are done at the Berwick studio, where the paint can be sealed clean and cured without salt in the air."),
        ("I tow a boat. Anything I should know?", "Rinse the lower panels, wheels and the tow bar area after every ramp run. Coated wheels and sills make that rinse far more effective."),
        ("Will a coating stop rust?", "It will not fix existing rust, and it cannot seal a chip that is already through to metal. It does slow corrosion by keeping salt off intact paint."),
        ("Can you get sand out of the interior?", "Yes - a proper interior detail gets sand out of seat rails, carpet and vents, and a fabric coating makes the next lot easier to vacuum."),
    ],
},

# ---------------------------------------------------------------------------
"hills": {
    "label": "The Dandenong Ranges and hills",
    "intros": [
        "Cars in {suburb} live under trees. Tall canopy means constant shade and damp, "
        "and with it eucalypt sap, leaf litter and bark that sit on the paint and hold "
        "moisture against it for days.",

        "The hills are beautiful and hard on paint. In {suburb} a car spends most of its "
        "life in the shade of big trees, rarely fully dries after rain, and collects sap, "
        "moss and debris faster than almost anywhere else we service.",

        "Driving out of {suburb} means winding roads, dappled shade and a car that is "
        "never quite dry. Sap etches, leaf stain marks light paint, and the damp gives "
        "everything longer to bite. Sealing the paint is what stops it keying in.",
    ],
    "conditions": [
        ("Eucalypt sap", "Gum sap is sticky and acidic. On a warm day it sets hard and etches a ring into the clear coat that no wash will remove."),
        ("Leaf litter and tannin stains", "Wet leaves sitting in the scuttle panel, on the roof or in door shuts leave brown tannin stains, especially on white and silver paint."),
        ("Constant shade and damp", "Shade keeps the car wet for longer after rain and morning fog, which gives sap, droppings and fallout far more time to bite."),
        ("Moss and mould in the seals", "Cars parked under canopy grow moss in window rubbers and panel gaps, and mould inside if they are left closed and damp."),
        ("Bark and twigs on the roof", "Falling bark and small branches scratch roofs and bonnets, and dropped debris in the cowl blocks drains."),
        ("Winding roads and grit", "Mountain roads throw up grit and leaf debris into sills and wheels, and tight corners mean a lot of kerbed rims."),
        ("Bird life", "The Ranges are full of birds, which means frequent droppings on cars parked under trees. Coated paint lets you remove them before they etch."),
        ("Fog on the glass", "Fog and damp leave a film on the windscreen that makes wet-weather and night driving harder. Coated glass stays clearer and sheds water."),
    ],
    "faqs": [
        ("Can a coating stop sap damage?", "It will not stop sap landing, but it stops it bonding. On sealed paint you can lift sap off safely instead of finding an etched ring days later. Existing rings are polished out first."),
        ("My white car has brown marks from leaves. Can they come out?", "Usually. Tannin staining responds well to decontamination and a polish, and a coating makes it much harder for new stains to set."),
        ("How far is the studio from {suburb}?", "About {km} km. Coatings are applied at the Berwick studio, out of the damp, so they can cure properly - the one place a hills car does not want to be during a cure is under a wet canopy."),
        ("What about moss in the window rubbers?", "We clean seals and door shuts as part of a proper detail, and treating the rubbers helps stop it coming back."),
        ("Is it worth coating a car that lives under trees?", "More than almost anywhere else. Shade, damp and sap are exactly the conditions a coating is built to handle."),
        ("Can you do the glass?", "Yes, and in the hills it is one of the most useful things we do - coated glass sheds fog and rain far better."),
        ("Do you fix kerbed wheels?", "We clean, decontaminate and coat wheels. Kerb damage to the rim itself is a wheel-repair job, and we will point you to someone good."),
    ],
},

# ---------------------------------------------------------------------------
"acreage": {
    "label": "Lifestyle acreage",
    "intros": [
        "{suburb} is big blocks and long gravel driveways, and that means dust. A fine "
        "abrasive film settles on the car every time it moves, and it is the reason "
        "acreage cars get scratched by the very act of cleaning them.",

        "Acreage living around {suburb} is hard on a car's finish: unsealed drives, "
        "dirt roads, sheds, horse floats and the ute that does the real work. Most of "
        "the damage we see is from grit - and grit is exactly what a coating is best at "
        "shrugging off.",

        "Out around {suburb}, a car is rarely clean for long. The goal is not a car that "
        "never gets dusty; it is a car that can be rinsed clean safely instead of wiped, "
        "because wiping dust off dry paint is how it gets scratched.",
    ],
    "conditions": [
        ("Gravel-drive dust", "Every trip up an unsealed drive leaves a layer of fine, abrasive dust. Wiping it off dry is like using very fine sandpaper."),
        ("Stone chips from dirt roads", "Loose gravel flicks up into the front and the sills. Coatings do not stop impacts, but they seal the surrounding paint and make chips less of an entry point."),
        ("Utes that work", "Farm and trade utes carry dirt, feed, chemicals and tools. A coated tray, canopy and paint takes a fraction of the time to clean."),
        ("Horse floats and trailers", "Towing floats and trailers throws mud and grit up the back of the car and onto the tow bar area."),
        ("Mud in the arches", "Wet-season mud packs into wheel arches and sills and holds moisture against the metal."),
        ("Sun on open blocks", "Open acreage means little shade and a lot of UV, which fades paint and chalks plastic trim."),
        ("Sheds and farm dust", "Cars stored in sheds pick up hay dust, bird droppings from roosting birds and the odd rodent - interiors included."),
        ("Long kilometres", "Acreage means driving further for everything. Bugs, road film and stone chips add up faster than they do in the suburbs."),
    ],
    "faqs": [
        ("Is a coating worth it on a dusty property?", "Yes - it is one of the best places for one. Dust does not bond to sealed paint, so it rinses off instead of having to be wiped, which is what protects the finish."),
        ("Do you coat utes and 4WDs?", "Yes, including trays, canopies, bars and raw plastics. They benefit as much as the paint does."),
        ("Will a coating stop stone chips?", "No. Stone chips are impact damage and only paint protection film meaningfully reduces them. A coating seals the paint around them."),
        ("How far is the studio from {suburb}?", "About {km} km, in Berwick. The car comes in because a coating needs a clean, dust-free space to cure - a gravel drive is the opposite."),
        ("Can you clean out a car that lives in a shed?", "Yes. Interior detailing handles dust, droppings and odour, and coating the fabric makes it easier to keep clean afterwards."),
        ("How should I wash a car that gets dusty every day?", "Rinse first with plenty of water to lift the grit, then wash - never wipe dust off dry. On coated paint the rinse does most of the job."),
        ("Can you coat the wheels?", "Yes, and on dirt roads it is well worth it - brake dust and mud stop baking onto coated wheels."),
    ],
},

# ---------------------------------------------------------------------------
"rural": {
    "label": "Farming flats and country towns",
    "intros": [
        "{suburb} is farming country - flat, open, and served by roads that are dusty in "
        "summer and muddy in winter. Cars and utes here cover real distances, and it "
        "shows in the paint, the wheels and the interior.",

        "Around {suburb}, vehicles are tools first. They carry feed and tools, run farm "
        "tracks and highways in the same day, and are rarely garaged. That is honest "
        "wear, and most of it can be cleaned up and protected.",

        "Country driving out of {suburb} means long kilometres, road film, bugs and "
        "whatever the season throws up from the paddocks. The value of a coating here "
        "is simple: the vehicle stays cleaner, cleans up faster, and holds its value "
        "better.",
    ],
    "conditions": [
        ("Farm tracks and dust", "Summer dust coats everything and gets into door seals and vents. It is abrasive, so it has to be rinsed, not wiped."),
        ("Winter mud", "Wet-season mud packs into arches, sills and underbodies and holds moisture against the metal."),
        ("Bug strike on the highway", "Long highway runs leave bug residue on the front end and glass. It is acidic and etches if left; coated paint releases it easily."),
        ("Fertiliser and chemical splash", "Farm chemicals and fertiliser dust are harsh on paint and trim. Sealing the surface keeps them from getting a grip."),
        ("Utes and working vehicles", "Trays, canopies and tool boxes take a beating. Coating them makes the weekly clean-up far quicker."),
        ("Outdoor parking all year", "Most farm vehicles live outside, taking full sun and weather. UV fade and chalky trim are the result."),
        ("Stone chips from gravel roads", "Gravel roads chip the front and sills. A coating does not stop chips but helps protect the paint around them."),
        ("Resale on a working vehicle", "A work ute that has been protected sells for noticeably more than one with sun-baked paint and a stained interior."),
    ],
    "faqs": [
        ("Is the drive to the studio worth it from {suburb}?", "It is about {km} km to Berwick. A coating is a one-off job that protects the vehicle for years, and it needs a controlled space to cure - which is why it is done in the studio."),
        ("Do you coat farm utes?", "Yes - paint, trays, canopies and trim. A coated ute rinses clean after a day on the tracks."),
        ("Can you get bug marks off the front?", "Fresh bug residue comes off easily; etched marks can usually be polished out. On coated paint they barely stick."),
        ("Will a coating help with the mud and dust?", "Yes. Neither bonds to sealed paint the way it does to bare clear coat, so a hose does most of the cleaning."),
        ("Can you clean up a working interior?", "Yes. We deep-clean seats, carpets and trim, and coat the fabric so dirt and spills are easier to deal with next time."),
        ("What about chalky, faded trim?", "Faded plastic trim can usually be restored and then coated so it does not go grey again."),
        ("How long will the vehicle be off the road?", "Most jobs are one to three days. We can plan around harvest or busy periods if you tell us when you book."),
    ],
},
}


# The 40 km expansion added archetypes for the inner south-east and the Yarra Valley.
from content_pool_40 import EXTRA as _EXTRA_40
ARCHETYPES.update(_EXTRA_40)


# ------------------------------------------------------------------ rotation
def fnv1a(s):
    """FNV-1a 32-bit. Stable across builds and Python versions (hash() is not)."""
    h = 0x811C9DC5
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def pick(pool, n, slug, salt=""):
    """Take n items from pool, rotating by a hash of the slug.

    Rotating (rather than shuffling) keeps the reading order sensible while giving
    neighbouring suburbs different sets.
    """
    if not pool:
        return []
    n = min(n, len(pool))
    start = fnv1a(slug + salt) % len(pool)
    return [pool[(start + i) % len(pool)] for i in range(n)]


def pick_one(pool, slug, salt=""):
    return pick(pool, 1, slug, salt)[0]
