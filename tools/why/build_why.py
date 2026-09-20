# -*- coding: utf-8 -*-
"""Writes the album gallery into index.html's #why-ceramic section, between
<!--WHY-GALLERY-START--> and <!--WHY-GALLERY-END--> (inserted above .why-grid on first run).
   usage: python tools/why/build_why.py          (after convert.py)
Edit albums.py, never the generated block."""
import io, os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
from albums import ALBUMS
JSV = "1"
A, B = "<!--WHY-GALLERY-START-->", "<!--WHY-GALLERY-END-->"
esc = lambda t: html.escape(t, quote=True)
CHEV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="%s"/></svg>'
L, R = CHEV % "M15 6l-6 6 6 6", CHEV % "M9 6l6 6-6 6"
ZOOM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'

def block():
    o = [A, '    <div class="wg reveal" data-wg>', '      <div class="wg-bar">',
         '        <div class="wg-tabs" role="tablist" aria-label="Ceramic coating guides by vehicle">']
    for i, (slug, name, sub, slides) in enumerate(ALBUMS):
        o.append('          <button type="button" class="wg-tab%s" role="tab" id="wg-t-%s" aria-controls="wg-p-%s" aria-selected="%s" data-name="%s"%s>%s <i>%d</i></button>'
                 % (" is-on" if i == 0 else "", slug, slug, "true" if i == 0 else "false", esc(name), "" if i == 0 else ' tabindex="-1"', esc(name), len(slides)))
    o += ['        </div>', '        <div class="wg-nav">',
          '          <span class="wg-count" aria-live="polite"><b>01</b> / %02d</span>' % len(ALBUMS[0][3]),
          '          <button type="button" class="wg-arrow" data-dir="-1" aria-label="Previous slide" disabled>%s</button>' % L,
          '          <button type="button" class="wg-arrow" data-dir="1" aria-label="Next slide">%s</button>' % R,
          '        </div>', '      </div>']
    for i, (slug, name, sub, slides) in enumerate(ALBUMS):
        o.append('      <div class="wg-panel" role="tabpanel" id="wg-p-%s" aria-labelledby="wg-t-%s"%s>' % (slug, slug, "" if i == 0 else " hidden"))
        o.append('        <p class="wg-cap"><b>%s</b> %s <span>Tap a slide to read it full size</span></p>' % (esc(name), esc(sub)))
        o.append('        <ul class="wg-track" tabindex="0" aria-label="%s: %s">' % (esc(name), esc(sub)))
        for k, (_, word, head) in enumerate(slides, 1):
            o.append('          <li class="wg-slide"><a href="assets/why/%s-%02d.webp" data-cap="%s"><img src="assets/why/%s-%02d-s.webp" alt="%s" width="640" height="800" loading="lazy" decoding="async"><span class="wg-zoom">%s</span></a></li>'
                     % (slug, k, esc(head), slug, k, esc(name + " - " + head), ZOOM))
        o += ['        </ul>', '      </div>']
    o += ['      <div class="wg-progress" aria-hidden="true"><span></span></div>', '    </div>',
          '    <dialog class="wg-lb" aria-label="Slide viewer" tabindex="-1">',
          '      <button type="button" class="wg-lb-x" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>',
          '      <button type="button" class="wg-lb-a" data-dir="-1" aria-label="Previous slide">%s</button>' % L,
          '      <figure><img alt="" width="1122" height="1402"><figcaption><b class="wg-lb-meta"></b><span class="wg-lb-text"></span></figcaption></figure>',
          '      <button type="button" class="wg-lb-a" data-dir="1" aria-label="Next slide">%s</button>' % R,
          '    </dialog>', '    ' + B]
    return "\n".join(o)

def main():
    p = os.path.join(ROOT, "index.html"); s = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"; blk = block().replace("\n", nl)
    if A in s:
        s = s[:s.index(A)] + blk + s[s.index(B) + len(B):]
    else:
        anchor = '<div class="why-grid reveal">'; assert s.count(anchor) == 1
        s = s.replace(anchor, blk + nl + nl + "    " + anchor)
    tag = '<script src="js/why-gallery.js?v=%s"></script>' % JSV
    if "js/why-gallery.js" not in s:
        after = '<script src="js/beforeafter.js"></script>'; assert s.count(after) == 1
        s = s.replace(after, after + nl + tag)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    n = sum(len(a[3]) for a in ALBUMS)
    missing = [f for a in ALBUMS for k in range(1, len(a[3]) + 1) for f in ("%s-%02d.webp" % (a[0], k), "%s-%02d-s.webp" % (a[0], k)) if not os.path.exists(os.path.join(ROOT, "assets", "why", f))]
    print("index.html: %d albums, %d slides written | missing image files: %s" % (len(ALBUMS), n, missing or "none"))

if __name__ == "__main__":
    main()
