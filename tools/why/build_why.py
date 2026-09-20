# -*- coding: utf-8 -*-
"""Writes the #why-ceramic poster (headline, eight reason pills, mixed-album carousels, lightbox)
into index.html between <!--WHY-GALLERY-START--> and <!--WHY-GALLERY-END-->.
   usage: python tools/why/build_why.py          (after convert.py)
Edit albums.py, never the generated block. The section's honest "Straight up" note and its CTA
sit after the END marker and are hand-written."""
import io, os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
from albums import ALBUMS, REASONS
JSV = "2"
A, B = "<!--WHY-GALLERY-START-->", "<!--WHY-GALLERY-END-->"
esc = lambda t: html.escape(t, quote=True)
CHEV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="%s"/></svg>'
L, R = CHEV % "M15 6l-6 6 6 6", CHEV % "M9 6l6 6-6 6"
ZOOM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'
BY = {a[0]: a for a in ALBUMS}

def check():
    every = {(a[0], k) for a in ALBUMS for k in range(1, len(a[3]) + 1)}
    used = {s for r in REASONS for s in r[4]}
    assert not (used - every), "REASONS points at slides that do not exist: %s" % sorted(used - every)
    assert not (every - used), "slides in no reason (they would vanish from the site): %s" % sorted(every - used)

def block():
    n_slides = sum(len(a[3]) for a in ALBUMS)
    o = [A,
         '    <header class="wp-head reveal">',
         '      <div class="wp-meta"><span class="wb-kicker">Why ceramic coating</span><span class="wp-issue">Eight reasons<i>/</i>%d slides<i>/</i>four cars</span></div>' % n_slides,
         '      <h2 class="h-sec wp-title">More than a shine.<br><em>Real protection.</em></h2>',
         '      <p class="lede wp-lede">A ceramic coating bonds to your clear coat as a hard, ultra-slick sacrificial layer. Here are the eight reasons owners get it done &mdash; pick one, swipe the slides, tap any of them to read it full size.</p>',
         '    </header>',
         '    <div class="wg reveal" data-wg>',
         '      <div class="wg-tabs" role="tablist" aria-label="Eight reasons to ceramic coat a car">']
    for i, (title, pill, ghost, copy, refs) in enumerate(REASONS):
        o.append('        <button type="button" class="wg-tab%s" role="tab" id="wg-t-%d" aria-controls="wg-p-%d" aria-selected="%s" data-name="%s" data-ghost="%s"%s><i>%02d</i>%s</button>'
                 % (" is-on" if i == 0 else "", i + 1, i + 1, "true" if i == 0 else "false", esc(title), esc(ghost), "" if i == 0 else ' tabindex="-1"', i + 1, esc(pill)))
    o += ['      </div>', '      <div class="wg-stage">', '        <div class="wg-ghost" aria-hidden="true">%s</div>' % esc(REASONS[0][2])]
    for i, (title, pill, ghost, copy, refs) in enumerate(REASONS):
        o.append('        <div class="wg-panel" role="tabpanel" id="wg-p-%d" aria-labelledby="wg-t-%d"%s>' % (i + 1, i + 1, "" if i == 0 else " hidden"))
        o.append('          <div class="wg-why"><span class="wg-no" aria-hidden="true">%02d</span><div><h3>%s</h3><p>%s</p></div></div>' % (i + 1, esc(title), esc(copy)))
        o.append('          <ul class="wg-track" tabindex="0" aria-label="%s: slides">' % esc(title))
        for k, (slug, idx) in enumerate(refs):
            name = BY[slug][1]; head = BY[slug][3][idx - 1][2]
            o.append('            <li class="wg-slide" style="--i:%d"><a href="assets/why/%s-%02d.webp" data-cap="%s"><img src="assets/why/%s-%02d-s.webp" alt="%s" width="640" height="800" loading="lazy" decoding="async"><span class="wg-zoom">%s</span></a><span class="wg-fig"><b>%02d</b>%s</span></li>'
                     % (min(k, 5), slug, idx, esc(name + ": " + head), slug, idx, esc(name + " - " + head), ZOOM, k + 1, esc(name)))
        o += ['          </ul>', '        </div>']
    o += ['        <div class="wg-foot">', '          <div class="wg-progress" aria-hidden="true"><span></span></div>',
          '          <div class="wg-nav">',
          '            <span class="wg-count" aria-live="polite"><b>01</b> / %02d</span>' % len(REASONS[0][4]),
          '            <button type="button" class="wg-arrow" data-dir="-1" aria-label="Previous slide" disabled>%s</button>' % L,
          '            <button type="button" class="wg-arrow" data-dir="1" aria-label="Next slide">%s</button>' % R,
          '          </div>', '        </div>', '      </div>', '    </div>',
          '    <dialog class="wg-lb" aria-label="Slide viewer" tabindex="-1">',
          '      <button type="button" class="wg-lb-x" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>',
          '      <button type="button" class="wg-lb-a" data-dir="-1" aria-label="Previous slide">%s</button>' % L,
          '      <figure><img alt="" width="1122" height="1402"><figcaption><b class="wg-lb-meta"></b><span class="wg-lb-text"></span></figcaption></figure>',
          '      <button type="button" class="wg-lb-a" data-dir="1" aria-label="Next slide">%s</button>' % R,
          '    </dialog>', '    ' + B]
    return "\n".join(o)

def main():
    check()
    p = os.path.join(ROOT, "index.html"); s = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"; blk = block().replace("\n", nl)
    sec = s.index('id="why-ceramic"'); note = s.index('<div class="why-note', sec)
    if A in s:
        a = s.index(A)
        head = s.find('<div class="sec-head reveal">', sec, a)        # v1 left the old heading above the marker
        start = head if head != -1 else a
    else:
        start = s.index('<div class="sec-head reveal">', sec)
    # everything from the heading to the note is generated: the old 8-card .why-grid goes too
    s = s[:start] + blk.lstrip() + nl + nl + "    " + s[note:]
    import re
    s = re.sub(r'<script src="js/why-gallery\.js\?v=\d+"></script>', '<script src="js/why-gallery.js?v=%s"></script>' % JSV, s)
    assert "js/why-gallery.js?v=%s" % JSV in s
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("index.html: %d reasons, %d carousel entries over %d unique slides | why-grid left: %d"
          % (len(REASONS), sum(len(r[4]) for r in REASONS), sum(len(a[3]) for a in ALBUMS), s.count('class="why-grid')))

if __name__ == "__main__":
    main()
