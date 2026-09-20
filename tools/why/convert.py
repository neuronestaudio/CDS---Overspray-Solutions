# -*- coding: utf-8 -*-
"""PNG album slides (1122x1402, ~2.2 MB each) -> WebP in assets/why/ (about 40% of the JPEG weight).
   usage: python tools/why/convert.py "<folder holding the extracted PNGs>"
Two sizes per slide: -s (640 wide, the carousel) and full (1122 wide, the lightbox)."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from albums import ALBUMS, SOURCE_NAME
src = sys.argv[1]; root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."); out = os.path.join(root, "assets", "why")
os.makedirs(out, exist_ok=True); total = 0
for slug, _, _, slides in ALBUMS:
    for i, (num, _, _) in enumerate(slides, 1):
        im = Image.open(os.path.join(src, "%s %02d.png" % (SOURCE_NAME[slug], num))).convert("RGB")
        for suffix, w, q in (("", 1122, 82), ("-s", 640, 78)):
            t = im if w == im.width else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            p = os.path.join(out, "%s-%02d%s.webp" % (slug, i, suffix)); t.save(p, "WEBP", quality=q, method=6); total += os.path.getsize(p)
    print("%-8s %2d slides" % (slug, len(slides)))
print("assets/why: %.1f MB total" % (total / 1e6))
