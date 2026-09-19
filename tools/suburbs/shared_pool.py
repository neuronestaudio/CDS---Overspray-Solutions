# -*- coding: utf-8 -*-
"""Rotating variants for the blocks that would otherwise be byte-identical on every
suburb page: the lede, the owner paragraph, section headings, the process steps
and the CTA line.

On the Ronin build, rotating these took the worst same-archetype pair from 0.78 to
0.62 - more than widening the archetype pools did. Placeholders: {suburb}, {pc},
{km}.
"""

LEDES = [
    "Ceramic coating, paint correction and paint protection for {suburb} {pc}, applied at "
    "our controlled, dust-free studio in Berwick, about {km} km away.",
    "GYEON and ONYX ceramic coatings, machine paint correction and overspray removal for "
    "{suburb} drivers, done properly in our Berwick studio ({km} km from {suburb}).",
    "Professional paint protection for {suburb} {pc}: decontamination, correction and a "
    "certified coating, all carried out at the CDS studio in Berwick.",
    "From swirl removal to a multi-year graphene coating, {suburb} cars are looked after "
    "at our Berwick studio, roughly {km} km up the road.",
]

OWNER = [
    "Every {suburb} booking is handled by Andy himself &mdash; owner-operated, 30+ years "
    "on paint, and the same standard for a daily driver, a work ute or a weekend car. "
    "Tell us the car and what is bothering you and you will get a straight answer.",
    "There is no sales team and no subcontracting. Andy assesses, corrects and coats "
    "every car from {suburb} himself, with more than thirty years on paint behind him, "
    "and will tell you honestly if a job is not worth doing.",
    "CDS is owner-operated. The person who looks at your paint is the person who "
    "corrects and coats it &mdash; Andy, with 30+ years of experience &mdash; so what "
    "you are quoted for {suburb} is exactly what gets done.",
]

H_LOCAL = [
    "Local to {suburb}",
    "Looking after cars in {suburb}",
    "{suburb}, and what it does to paint",
]
H_COND = [
    "What your paint is up against in {suburb}.",
    "What {suburb} does to a car&rsquo;s finish.",
    "The things that wear paint down in {suburb}.",
    "Local conditions in {suburb}, and how we handle them.",
]
H_SERV = [
    "Ceramic coating services for {suburb}.",
    "What we do for {suburb} cars.",
    "Paint protection services near {suburb}.",
]
H_PROC = [
    "How a {suburb} booking runs.",
    "From drop-off to pick-up.",
    "What happens when your car comes in.",
]
H_FAQ = [
    "{suburb} ceramic coating questions.",
    "Questions we get from {suburb}.",
    "Before you book from {suburb}.",
]
H_NEAR = [
    "Also servicing near {suburb}.",
    "Suburbs around {suburb} we look after.",
    "Close to {suburb}.",
]
CTA = [
    "Protect your paint in {suburb}",
    "Book your {suburb} car in",
    "Get a straight quote for your car",
    "Sort your paint out properly",
]

# Three complete four-step process strips, each accurate to how the studio works.
PROCESS = [
    [("01", "Assessment", "We inspect the paint under proper lighting and measure the clear coat, then tell you what it actually needs."),
     ("02", "Decontaminate", "Iron-fallout treatment and a clay strip, so nothing is ever sealed in under the coating."),
     ("03", "Correct", "Machine polishing in measured stages to remove swirls and etching rather than fill them."),
     ("04", "Coat &amp; cure", "GYEON or ONYX applied and cured in a controlled, dust-free space, with the warranty registered.")],
    [("01", "Look and measure", "Paint depth readings and a close look under the lights before anything touches the car."),
     ("02", "Deep clean", "A full wash, then chemical and clay decontamination to strip out what washing leaves behind."),
     ("03", "Polish", "Correction matched to your paint - gentler on soft clear coats, more passes on hard ones."),
     ("04", "Seal", "The coating goes on panel by panel and cures indoors before the car goes home.")],
    [("01", "Honest quote", "You get a straight assessment of what the paint needs, and what it does not."),
     ("02", "Prep", "Wash, iron treatment and clay, so the surface is genuinely clean before it is corrected."),
     ("03", "Refine", "Swirls, holograms and etching are levelled out by machine, measured as we go."),
     ("04", "Protect", "A certified coating, a proper cure, a registered warranty and a simple wash routine.")],
]

SERVICES = [
    ("ceramic-coating-melbourne.html", "Ceramic &amp; graphene coating"),
    ("graphene-coating-melbourne.html", "Graphene coating"),
    ("paint-correction-melbourne.html", "Paint correction"),
    ("swirl-mark-removal-melbourne.html", "Swirl &amp; scratch removal"),
    ("overspray-removal-melbourne.html", "Overspray removal"),
    ("industrial-fallout-removal-melbourne.html", "Industrial fallout removal"),
    ("wheel-glass-interior-coating.html", "Wheel, glass &amp; interior coating"),
    ("new-car-paint-protection-melbourne.html", "New car protection"),
    ("ute-4wd-ceramic-coating-melbourne.html", "Ute &amp; 4WD coating"),
    ("ceramic-coating-maintenance.html", "Coating maintenance"),
]
