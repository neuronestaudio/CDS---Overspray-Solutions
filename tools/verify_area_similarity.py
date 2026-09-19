# -*- coding: utf-8 -*-
"""Measure how similar the generated suburb pages are to each other.

WHY THIS EXISTS
---------------
This site ships ~160 pages built from one template, one per south-east Melbourne
suburb (``ceramic-coating-<slug>.html`` in the repo root). That is exactly the shape
of a doorway-page network: many near-identical pages, each aimed at a different
place name. Google filters those, and the filtering is silent - the pages stay
indexed-ish, they just never rank, so nothing in the build tells you it went
wrong.

The defence is the content pool in ``tools/suburbs/content_pool.py``: each
archetype has more intros / conditions / FAQs than any one page renders, and
each page picks its set from a hash of its own slug. That defence is easy to
destroy by accident - trim a pool, drop a variant, reuse one FAQ everywhere -
and the site will still build, still validate, and still look fine in a browser.

So this script measures the thing the pool is supposed to buy, and fails loudly
in CI when it stops being true.

HOW IT MEASURES
---------------
* Only the unique region of each page is read: the text between the generated
  ``<!--PAGE-BODY-START-->`` and ``<!--PAGE-BODY-END-->`` markers. The shared
  nav, footer and mobile call bar are identical on every page by design; letting
  them into the comparison would flatter every number and hide real duplication.
* Each page's visible text is reduced to a set of 7-word shingles (7-grams).
  Two pages that share a long run of words share that shingle; swapping only the
  suburb name breaks 7 shingles and leaves the rest, which is the point.
* Pages are only compared against pages of the SAME archetype. Comparing a
  coastal page to a mountains page tells you nothing - they were always going to
  differ - and mixing them into the mean drags the average down until a genuinely
  duplicated cluster looks acceptable.
* Score is Jaccard similarity on those sets: |A n B| / |A u B|.

HOW TO READ THE NUMBERS
-----------------------
* ``0.30 - 0.55`` is the healthy band for same-archetype pages. They share a
  template and a topic, so a real overlap is expected and fine.
* ``0.55 - 0.72`` is worth a look. Usually means one page's slug hash landed on
  nearly the same pool picks as its neighbour's.
* ``> 0.72`` is a FAIL. At that point the two pages are the same page with the
  place name swapped, which is the doorway pattern this build is trying not to be.

Exit status is 1 if any same-archetype pair exceeds the threshold, else 0, so
this can sit in CI as-is.

Usage:
    python tools/verify_area_similarity.py
    python tools/verify_area_similarity.py --max 0.65 --quiet
"""

import argparse
import html
import io
import itertools
import os
import re
import sys
from hashlib import blake2b

# ----------------------------------------------------------------- constants

PAGE_GLOB = "ceramic-coating-*.html"
BODY_START = "<!--PAGE-BODY-START-->"
BODY_END = "<!--PAGE-BODY-END-->"
SHINGLE_SIZE = 7
DEFAULT_MAX = 0.72
DEFAULT_TOP = 10

# Pages this short are almost certainly a generator failure rather than a real
# page, and they make Jaccard behave strangely (tiny sets swing to 0 or 1).
MIN_TOKENS_WARN = 120

NO_ARCHETYPE = "(no-archetype-meta)"

_RE_DROP_BLOCKS = re.compile(r"<(script|style|svg)\b[^>]*>.*?</\1\s*>", re.I | re.S)
_RE_DROP_BLOCKS_UNCLOSED = re.compile(r"<(script|style|svg)\b[^>]*>.*\Z", re.I | re.S)
_RE_COMMENT = re.compile(r"<!--.*?-->", re.S)
_RE_TAG = re.compile(r"<[^>]*>", re.S)
_RE_WS = re.compile(r"\s+")
_RE_TOKEN = re.compile(r"[0-9a-z]+(?:'[0-9a-z]+)?")
_RE_META = re.compile(r"<meta\b[^>]*>", re.I)
_RE_ATTR = re.compile(r"""\b(name|content)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)


# ------------------------------------------------------------------ extraction

def meta_value(source, meta_name):
    """Return the ``content`` of ``<meta name="meta_name" ...>``, or None.

    Attribute order is not assumed, and either quote style is accepted.
    """
    wanted = meta_name.lower()
    for tag in _RE_META.findall(source):
        attrs = {}
        for m in _RE_ATTR.finditer(tag):
            key = m.group(1).lower()
            val = m.group(3) if m.group(3) is not None else (
                m.group(4) if m.group(4) is not None else m.group(5))
            attrs[key] = (val or "").strip()
        if attrs.get("name", "").lower() == wanted and "content" in attrs:
            return attrs["content"]
    return None


def body_region(source):
    """Return the raw HTML between the PAGE-BODY markers, or None if absent.

    Absent markers mean the page was not produced by the current generator, so
    the caller skips the file and warns rather than silently comparing chrome.
    """
    start = source.find(BODY_START)
    if start < 0:
        return None
    end = source.find(BODY_END, start + len(BODY_START))
    if end < 0:
        return None
    return source[start + len(BODY_START):end]


def visible_text(fragment):
    """Reduce an HTML fragment to collapsed, lowercased visible text."""
    text = _RE_DROP_BLOCKS.sub(" ", fragment)
    # A <script>/<style>/<svg> left open by a truncated fragment would otherwise
    # leak its source into the comparison.
    text = _RE_DROP_BLOCKS_UNCLOSED.sub(" ", text)
    text = _RE_COMMENT.sub(" ", text)
    text = _RE_TAG.sub(" ", text)
    text = html.unescape(text)
    return _RE_WS.sub(" ", text).strip().lower()


def tokenise(text):
    """Split normalised text into comparable word tokens."""
    return _RE_TOKEN.findall(text)


def shingles(tokens, size=SHINGLE_SIZE):
    """Hash every n-gram to a 64-bit int and return the set.

    Hashing keeps memory flat (414 pages x ~1k shingles) and set intersection
    cheap, and blake2b is used instead of the builtin hash() so two runs of this
    script produce byte-identical reports.
    """
    if not tokens:
        return frozenset()
    if len(tokens) < size:
        grams = [" ".join(tokens)]
    else:
        grams = (" ".join(tokens[i:i + size]) for i in range(len(tokens) - size + 1))
    return frozenset(
        int.from_bytes(blake2b(g.encode("utf-8"), digest_size=8).digest(), "big")
        for g in grams
    )


def jaccard(a, b):
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a) + len(b) - inter
    return inter / union if union else 0.0


# -------------------------------------------------------------------- loading

class Page(object):
    __slots__ = ("filename", "slug", "archetype", "tokens", "grams")

    def __init__(self, filename, slug, archetype, tokens, grams):
        self.filename = filename
        self.slug = slug
        self.archetype = archetype
        self.tokens = tokens
        self.grams = grams


def slug_from_filename(filename):
    base = os.path.basename(filename)
    base = base[:-len(".html")] if base.lower().endswith(".html") else base
    prefix = "ceramic-coating-"
    return base[len(prefix):] if base.startswith(prefix) else base


def load_pages(root, size):
    """Read every suburb page under ``root``. Returns (pages, warnings)."""
    import glob as _glob

    paths = sorted(_glob.glob(os.path.join(root, PAGE_GLOB)))
    pages, warnings = [], []

    for path in paths:
        name = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read()
        except OSError as exc:
            warnings.append("%s: could not be read (%s)" % (name, exc))
            continue

        fragment = body_region(source)
        if fragment is None and meta_value(source, "x-suburb") is None:
            continue  # a hand-built ceramic-coating-* landing page, not a suburb page
        if fragment is None:
            warnings.append(
                "%s: no %s / %s markers - skipped (not generated by the current "
                "template?)" % (name, BODY_START, BODY_END))
            continue

        archetype = meta_value(source, "x-archetype")
        if not archetype:
            # Not skipped: a generator bug that drops the meta must not be able
            # to hide duplicate pages by removing them from the comparison.
            archetype = NO_ARCHETYPE
            warnings.append('%s: missing <meta name="x-archetype"> - grouped as %s'
                            % (name, NO_ARCHETYPE))

        slug = meta_value(source, "x-suburb")
        if not slug:
            slug = slug_from_filename(name)
            warnings.append('%s: missing <meta name="x-suburb"> - using filename '
                            'slug "%s"' % (name, slug))

        tokens = tokenise(visible_text(fragment))
        if len(tokens) < MIN_TOKENS_WARN:
            warnings.append("%s: only %d words between the body markers - too "
                            "short to score meaningfully" % (name, len(tokens)))

        pages.append(Page(name, slug, archetype, tokens, shingles(tokens, size)))

    return pages, warnings


# ------------------------------------------------------------------ comparison

def compare(pages, threshold):
    """Score every same-archetype pair.

    Returns (per_archetype, all_pairs). ``all_pairs`` is a list of
    (score, archetype, slug_a, slug_b) for every same-archetype pair.
    """
    by_archetype = {}
    for page in pages:
        by_archetype.setdefault(page.archetype, []).append(page)

    per_archetype = []
    all_pairs = []

    for archetype in sorted(by_archetype):
        group = sorted(by_archetype[archetype], key=lambda p: p.slug)
        scores = []
        worst = (-1.0, None, None)
        over = 0
        for a, b in itertools.combinations(group, 2):
            s = jaccard(a.grams, b.grams)
            scores.append(s)
            all_pairs.append((s, archetype, a.slug, b.slug))
            if s > worst[0]:
                worst = (s, a.slug, b.slug)
            if s > threshold:
                over += 1
        per_archetype.append({
            "archetype": archetype,
            "pages": len(group),
            "pairs": len(scores),
            "mean": (sum(scores) / len(scores)) if scores else 0.0,
            "max": worst[0] if scores else 0.0,
            "max_pair": (worst[1], worst[2]) if scores else None,
            "over": over,
        })

    return per_archetype, all_pairs


# --------------------------------------------------------------------- output

def force_utf8_stdout():
    """cp1252 consoles choke on the en dashes and curly quotes in the copy."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        try:
            if getattr(stream, "encoding", "").lower().replace("-", "") != "utf8":
                setattr(sys, stream_name,
                        io.TextIOWrapper(stream.buffer, encoding="utf-8",
                                         errors="replace", line_buffering=True))
        except (AttributeError, ValueError):
            pass  # redirected to something without a raw buffer; leave it alone


def build_parser():
    parser = argparse.ArgumentParser(
        prog="verify_area_similarity.py",
        description=(
            "Measure how similar the generated suburb pages are to each other, "
            "and fail if any two pages of the same archetype are near-duplicates. "
            "414 pages off one template is the doorway-page pattern; this is the "
            "check that catches a collapsed content pool before Google does."),
        epilog=(
            "Reads only the text between the <!--PAGE-BODY-START--> and "
            "<!--PAGE-BODY-END--> markers, so shared nav/footer chrome cannot "
            "flatter the score. Scoring is Jaccard on %d-word shingles, and pages "
            "are only compared within their own x-archetype. Healthy: 0.30-0.55. "
            "Look into it: 0.55-0.72. Fail: above the threshold. "
            "Exit status 1 on failure, 0 otherwise." % SHINGLE_SIZE),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--max", dest="threshold", type=float, default=DEFAULT_MAX, metavar="N",
        help="fail if any same-archetype pair scores above this "
             "(default: %.2f)" % DEFAULT_MAX)
    parser.add_argument(
        "--quiet", action="store_true",
        help="print only the summary, the failures and any warnings")
    parser.add_argument(
        "--top", type=int, default=DEFAULT_TOP, metavar="N",
        help="how many of the worst pairs to list (default: %d)" % DEFAULT_TOP)
    parser.add_argument(
        "--shingle", type=int, default=SHINGLE_SIZE, metavar="N",
        help="words per shingle; lower is stricter (default: %d)" % SHINGLE_SIZE)
    parser.add_argument(
        "--root", default=None, metavar="DIR",
        help="directory holding the %s pages "
             "(default: the repo root, i.e. this script's parent directory)"
             % PAGE_GLOB)
    return parser


def main(argv=None):
    force_utf8_stdout()
    args = build_parser().parse_args(argv)

    if args.shingle < 1:
        print("--shingle must be 1 or more")
        return 2
    if not (0.0 < args.threshold <= 1.0):
        print("--max must be between 0 and 1 (it is a Jaccard similarity)")
        return 2

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(args.root) if args.root else os.path.dirname(here)

    if not args.quiet:
        print("Suburb page similarity check")
        print("  root      : %s" % root)
        print("  pattern   : %s" % PAGE_GLOB)
        print("  shingle   : %d words" % args.shingle)
        print("  threshold : %.2f (same-archetype pairs only)" % args.threshold)
        print("")

    if not os.path.isdir(root):
        print("no pages found: %s does not exist" % root)
        return 0

    pages, warnings = load_pages(root, args.shingle)

    if not pages:
        print("no pages found matching %s in %s - nothing to compare"
              % (PAGE_GLOB, root))
        report_warnings(warnings)
        print("PASS: nothing to check (0 pages).")
        return 0

    per_archetype, all_pairs = compare(pages, args.threshold)
    failures = sorted((p for p in all_pairs if p[0] > args.threshold), reverse=True)
    overall_mean = (sum(p[0] for p in all_pairs) / len(all_pairs)) if all_pairs else 0.0
    overall_max = max(all_pairs)[0] if all_pairs else 0.0

    if not args.quiet:
        print("Per archetype")
        print("  %-22s %5s %7s %7s %7s  %s"
              % ("archetype", "pages", "pairs", "mean", "max", "worst pair"))
        for row in sorted(per_archetype, key=lambda r: r["max"], reverse=True):
            pair = ("%s / %s" % row["max_pair"]) if row["max_pair"] else "-"
            flag = "  <-- OVER (%d)" % row["over"] if row["over"] else ""
            print("  %-22s %5d %7d %7.3f %7.3f  %s%s"
                  % (row["archetype"], row["pages"], row["pairs"],
                     row["mean"], row["max"], pair, flag))
        print("")

        band_55 = sum(1 for p in all_pairs if 0.55 < p[0] <= args.threshold)
        print("Distribution")
        print("  same-archetype pairs compared : %d" % len(all_pairs))
        print("  mean similarity               : %.3f" % overall_mean)
        print("  max similarity                : %.3f" % overall_max)
        print("  pairs 0.55-%.2f (watch)        : %d" % (args.threshold, band_55))
        print("  pairs above %.2f (fail)        : %d" % (args.threshold, len(failures)))
        print("")

        top = sorted(all_pairs, reverse=True)[:max(args.top, 0)]
        if top:
            print("Worst %d pairs overall" % len(top))
            for score, archetype, a, b in top:
                mark = "FAIL" if score > args.threshold else "ok  "
                print("  %s %.3f  [%s]  %s  vs  %s" % (mark, score, archetype, a, b))
            print("")

    if failures:
        print("Pairs above the %.2f threshold (%d):" % (args.threshold, len(failures)))
        for score, archetype, a, b in failures[:200]:
            print("  %.3f  [%s]  %s  vs  %s" % (score, archetype, a, b))
        if len(failures) > 200:
            print("  ... and %d more" % (len(failures) - 200))
        print("")

    report_warnings(warnings)

    if failures:
        worst = failures[0]
        print("FAIL: %d of %d same-archetype pairs exceed %.2f - worst %.3f "
              "(%s vs %s, archetype %s). These pages are the same page with the "
              "suburb swapped; widen the content pool in "
              "tools/suburbs/content_pool.py."
              % (len(failures), len(all_pairs), args.threshold,
                 worst[0], worst[2], worst[3], worst[1]))
        return 1

    print("PASS: %d pages, %d same-archetype pairs, mean %.3f, worst %.3f, "
          "threshold %.2f."
          % (len(pages), len(all_pairs), overall_mean, overall_max, args.threshold))
    return 0


def report_warnings(warnings):
    if not warnings:
        return
    print("Warnings (%d):" % len(warnings))
    for line in warnings:
        print("  %s" % line)
    print("")


if __name__ == "__main__":
    sys.exit(main())
