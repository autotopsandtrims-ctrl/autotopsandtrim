"""Generate responsive WebP variants for every extracted photo.

A phone should never download a 800KB desktop image. This writes 480/800/1400px
wide variants next to each original and records real dimensions so every <img>
can carry width/height and avoid layout shift.
"""
import json
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = REPO
SCRATCH = HERE
ASSETS = os.path.join(REPO, "assets")
OUT_JSON = os.path.join(HERE, "images.json")


WIDTHS = [480, 800, 1400]
QUALITY = 80

catalog = {}
before = after = 0

names = sorted(
    f for f in os.listdir(ASSETS)
    if f.lower().endswith((".webp", ".jpg", ".jpeg", ".png"))
    and not any(f".-{w}." in f for w in WIDTHS)
)

for fname in names:
    path = os.path.join(ASSETS, fname)
    base, _ = os.path.splitext(fname)
    if base.endswith(("-480", "-800", "-1400")):
        continue

    before += os.path.getsize(path)
    with Image.open(path) as im:
        im = im.convert("RGB")
        ow, oh = im.size
        variants = []
        for w in WIDTHS:
            if w > ow:
                continue
            h = round(oh * w / ow)
            out_name = f"{base}-{w}.webp"
            out_path = os.path.join(ASSETS, out_name)
            im.resize((w, h), Image.LANCZOS).save(
                out_path, "WEBP", quality=QUALITY, method=6
            )
            variants.append({"w": w, "h": h, "file": out_name})
            after += os.path.getsize(out_path)

        # always have a largest usable variant
        if not variants:
            out_name = f"{base}-{ow}.webp"
            out_path = os.path.join(ASSETS, out_name)
            im.save(out_path, "WEBP", quality=QUALITY, method=6)
            variants.append({"w": ow, "h": oh, "file": out_name})
            after += os.path.getsize(out_path)

    catalog[base] = {"w": ow, "h": oh, "variants": variants}

with open(OUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(catalog, fh, indent=1)

print(f"photos processed : {len(catalog)}")
print(f"variants written : {sum(len(v['variants']) for v in catalog.values())}")
print(f"originals        : {before/1_048_576:.2f} MB")
print(f"variants total   : {after/1_048_576:.2f} MB")
smallest = sum(v["variants"][0]["file"] and os.path.getsize(
    os.path.join(ASSETS, v["variants"][0]["file"])) for v in catalog.values())
print(f"mobile tier (480) totals {smallest/1_048_576:.2f} MB across all photos")
