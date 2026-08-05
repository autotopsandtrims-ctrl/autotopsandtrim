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

bad = 0
for f in sorted(glob.glob("*.html")):
    html = open(f, encoding="utf-8").read()
    names = set(re.findall(r"assets/([a-z0-9\-]+?)-\d+\.webp", html))
    ident = collections.Counter(GROUPS.get(n, n) for n in names)
    dupes = {k: v for k, v in ident.items() if v > 1}
    if dupes:
        bad += 1
        print("REPEATED PHOTO on {}: {}".format(f, dupes))

print("distinct pages checked : {}".format(len(glob.glob("*.html"))))
print("pages repeating a photo: {}".format(bad))
