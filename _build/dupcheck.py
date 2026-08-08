"""Fail if any generated page shows the same photograph twice.

Duplicate groups come from the verified-content map in _build/build_pages.py:
17 files are really only 7 distinct images, so a page can repeat a photo while
referencing two different filenames.
"""
import re, glob, collections

GROUPS = {
    "g16-cadillac-convertible-red-interior": "CADILLAC",
    "headliner-install": "CADILLAC",
    "g17-cadillac-top-and-interior-finished": "CADILLAC",
    "hero-best-finished-vehicle-wide-full-color": "CADILLAC",
    "g09-truck-cab-black-seat-red-stitch": "F1-INTERIOR",
    "convertible-top-after": "F1-INTERIOR",
    "seat-rebuild-after": "BENCH-OUTDOORS",
    "process-header-photo-wide": "BENCH-OUTDOORS",
    "marine-seating-and-interior-upholstery": "RUNABOUT",
    "g22-marine-cushions-and-helm-trim": "RUNABOUT",
    "marine-boat-cushions-canvas": "RUNABOUT",
    "aircraft-interior-seat-upholstery": "AIRCRAFT-SEATS",
    "aviation-cabin-seats": "AIRCRAFT-SEATS",
    "custom-motorcycle-seat-upholstery-close-up": "CAFE-RACER",
    "motorcycle-custom-seat": "CAFE-RACER",
    "automotive-interior-restoration-detail": "BURGUNDY-TOP",
    "custom-bike-seat": "BURGUNDY-TOP",
}

# The old version collected names into a SET, so it could only ever catch the
# case above — the same photograph under two different filenames. A page that
# used one filename twice collapsed to a single set entry and passed, which is
# how the vinyl top ended up on the home page twice. Count occurrences instead.
#
# Two things have to be excluded or every page fails:
#   * the lightbox copies, which are a second <img> of a photo already shown.
#     They are emitted after </main>, so only the page body is scanned.
#   * srcset, which repeats the same basename once per tier. Only `src=` counts.
bad = 0
for f in sorted(glob.glob("*.html")):
    html = open(f, encoding="utf-8").read()
    body = html.split("</main>")[0]
    # The testimonial marquee prints its cards twice so the loop is seamless, so
    # every reviewer photo legitimately appears twice. Drop the whole marquee.
    body = re.sub(r'<div class="revmarquee".*?</div>\s*<div class="wrap"', '<div class="wrap"',
                  body, flags=re.S)
    names = re.findall(r'src="assets/([a-z0-9\-]+?)-\d+\.webp"', body)
    ident = collections.Counter(GROUPS.get(n, n) for n in names)
    dupes = {k: v for k, v in ident.items() if v > 1}
    if dupes:
        bad += 1
        print("REPEATED PHOTO on {}: {}".format(f, dupes))

print("distinct pages checked : {}".format(len(glob.glob("*.html"))))
print("pages repeating a photo: {}".format(bad))
