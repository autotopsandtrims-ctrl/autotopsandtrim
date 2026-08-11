"""Import a labelled folder of owner photos as EXCLUSIVE ad-page assets.

The owner supplies photos per ad landing page, foldered by page section:

    ads photos/Convertible Tops/before and after/       -> the pairs block
    ads photos/Convertible Tops/Tops out of this shop/  -> the photo strip
    ads photos/Auto Upholstery & Interiors/hero.jpg     -> the hero

Every import gets a basename prefixed for its page (ct-, au-, hl-, sr-, vt-) so
it can only ever appear on that one landing page. That is the whole point: these
are paid landing pages and the owner does not want them sharing photos with the
gallery, the blog or the home page. Overwriting an existing shared basename
would silently change up to five other pages.

iPhone HEIC is handled via pillow-heif. Phone photos are also frequently rotated
by EXIF only, which Pillow ignores unless told, so every image is transposed
before resizing — otherwise a portrait shot imports on its side.

    python _build\\import_ad_photos.py "<folder>" <prefix> [--dry]
"""
import json
import os
import re
import sys

from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:                                  # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ORIGINALS = os.path.join(REPO, "assets", "originals")
ASSETS = os.path.join(REPO, "assets")
CATALOG = os.path.join(HERE, "images.json")

WIDTHS = [480, 800, 1400]
QUALITY = 80
SRC_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif")


def natural(s):
    """Sort 'before 2' before 'before 10', and keep before/after paired."""
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", s)]


def build_variants(im, base):
    im = ImageOps.exif_transpose(im)
    alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
    im = im.convert("RGBA" if alpha else "RGB")
    ow, oh = im.size
    variants = []
    for w in WIDTHS:
        if w > ow:
            continue
        h = round(oh * w / ow)
        fn = "%s-%d.webp" % (base, w)
        im.resize((w, h), Image.LANCZOS).save(
            os.path.join(ASSETS, fn), "WEBP", quality=QUALITY, method=6)
        variants.append({"w": w, "h": h, "file": fn})
    if not variants:
        fn = "%s-%d.webp" % (base, ow)
        im.save(os.path.join(ASSETS, fn), "WEBP", quality=QUALITY, method=6)
        variants.append({"w": ow, "h": oh, "file": fn})
    return {"w": ow, "h": oh, "variants": variants}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    if len(args) < 2:
        print(__doc__)
        return 1
    folder, prefix = args[0], args[1]
    if not os.path.isdir(folder):
        print("no such folder: %s" % folder)
        return 1

    files = sorted(
        (f for f in os.listdir(folder) if f.lower().endswith(SRC_EXTS)),
        key=natural)
    if not files:
        print("no images in %s" % folder)
        return 1

    with open(CATALOG, encoding="utf-8") as fh:
        cat = json.load(fh)

    made = []
    for i, f in enumerate(files, 1):
        stem = os.path.splitext(f)[0].lower()
        stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
        # before/after folders keep their pairing legible in the basename;
        # everything else is just numbered in the order the folder sorts.
        m = re.match(r"^(before|after)-?(\d+)?$", stem)
        if m:
            base = "%s-%s%s" % (prefix, m.group(1), m.group(2) or "")
        else:
            base = "%s-%02d" % (prefix, i)
        src = os.path.join(folder, f)
        if dry:
            with Image.open(src) as im:
                im2 = ImageOps.exif_transpose(im)
                print("  %-42s -> %-26s %dx%d" % (f, base, im2.width, im2.height))
            made.append(base)
            continue
        with Image.open(src) as im:
            entry = build_variants(im, base)
        # keep a master so the site can be rebuilt from source later
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            im.convert("RGB").save(
                os.path.join(ORIGINALS, base + ".jpg"), "JPEG", quality=92)
        cat[base] = entry
        print("  %-42s -> %-26s %dx%d" % (f, base, entry["w"], entry["h"]))
        made.append(base)

    if not dry:
        with open(CATALOG, "w", encoding="utf-8") as fh:
            json.dump(cat, fh, indent=1)
    print("\n%d image(s) %s" % (len(made), "would import" if dry else "imported"))
    print("basenames: %s" % ", ".join(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
