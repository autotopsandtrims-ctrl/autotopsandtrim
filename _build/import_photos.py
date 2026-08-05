"""Triage a folder of raw shop photos into a labelled contact sheet.

Step 1 of the photo pipeline. Point it at a folder of dumped photos (the Google
Drive export, a phone dump, whatever) and it will:

  * read every image, whatever the extension actually claims
  * drop byte-identical duplicates
  * flag visually near-identical shots (burst frames, re-saves) as one group
  * fix EXIF rotation, which phone photos always need
  * write numbered review-size WebPs plus a contact sheet you can open and label

Nothing is copied into assets/ here — this step is purely "what have we got".
Once the user has labelled the numbers, run adopt_photos.py to move the keepers
into assets/ under real names, then make_responsive.py to cut the srcset tiers.

    python _build/import_photos.py --src "C:/path/to/downloaded/photos"
    # then open _build/incoming/contact-sheet.html

HEIC note: most "HEIC" files out of Google Drive are actually JPEG bytes with a
stale extension, and Pillow reads those fine. If a real HEIC turns up, install
pillow-heif (`pip install pillow-heif`) and rerun — it is picked up automatically.
"""
import argparse
import hashlib
import json
import os

from PIL import Image, ImageOps

try:                                    # optional, only needed for true HEIC
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF = True
except ImportError:
    HEIF = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "incoming")

REVIEW_W = 1400          # review copies; the real srcset tiers come later
THUMB_W = 400
QUALITY = 82
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff")


def dhash(im, size=16):
    """Difference hash — 256-bit perceptual fingerprint, no extra dependencies.

    Compares each pixel to its right-hand neighbour, so it keys on gradients
    rather than overall brightness. An average hash was tried first and grouped
    plainly different photos together whenever their overall luminance matched;
    dhash at 16x16 separates them cleanly.
    """
    g = im.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = g.tobytes()
    bits, i = 0, 0
    for row in range(size):
        base = row * (size + 1)
        for col in range(size):
            if px[base + col] > px[base + col + 1]:
                bits |= 1 << i
            i += 1
    return bits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder of raw photos")
    ap.add_argument("--near", type=int, default=12,
                    help="max differing bits (of 256) to call two shots near-identical; "
                         "raise to group more aggressively, lower to group less")
    args = ap.parse_args()

    if not os.path.isdir(args.src):
        raise SystemExit(f"source folder not found: {args.src}")
    os.makedirs(OUTDIR, exist_ok=True)

    files = sorted(f for f in os.listdir(args.src) if f.lower().endswith(EXTS))
    if not files:
        raise SystemExit(f"no images found in {args.src}")

    by_bytes, records, unreadable = {}, [], []
    exact_dupes = 0

    for fname in files:
        path = os.path.join(args.src, fname)
        with open(path, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        if digest in by_bytes:                       # same bytes, already have it
            by_bytes[digest]["dupe_names"].append(fname)
            exact_dupes += 1
            continue

        try:
            with Image.open(path) as im:
                real_format = im.format          # what it ACTUALLY is
                im = ImageOps.exif_transpose(im)  # phones lie about orientation
                im = im.convert("RGB")
                rec = {
                    "src": fname,
                    "sha256": digest[:16],
                    "format": real_format,
                    "w": im.width,
                    "h": im.height,
                    "bytes": os.path.getsize(path),
                    "dupe_names": [],
                    "phash": dhash(im),
                }
                rec["_im"] = im.copy()
                by_bytes[digest] = rec
                records.append(rec)
        except Exception as exc:                     # noqa: BLE001 - report, don't die
            unreadable.append((fname, f"{type(exc).__name__}: {exc}"))

    # group near-identical shots so the user labels a burst once, not eight times
    groups = []
    for rec in records:
        for g in groups:
            if bin(g[0]["phash"] ^ rec["phash"]).count("1") <= args.near:
                g.append(rec)
                break
        else:
            groups.append([rec])

    manifest, tiles = [], []
    for gi, group in enumerate(groups, 1):
        # keep the highest-resolution frame of a near-identical group as the lead
        group.sort(key=lambda r: r["w"] * r["h"], reverse=True)
        for within, rec in enumerate(group):
            num = f"{gi:03d}" if within == 0 else f"{gi:03d}{chr(96 + within)}"
            im = rec.pop("_im")
            w = min(REVIEW_W, im.width)
            h = round(im.height * w / im.width)
            out_name = f"{num}.webp"
            im.resize((w, h), Image.LANCZOS).save(
                os.path.join(OUTDIR, out_name), "WEBP", quality=QUALITY, method=6)

            entry = {k: v for k, v in rec.items() if k != "phash"}
            entry.update({"num": num, "group": gi, "review_file": out_name,
                          "lead_of_group": within == 0, "label": ""})
            manifest.append(entry)

            alt = " alt-of-group" if within else ""
            dupe_note = (f'<span class="d">{len(rec["dupe_names"])} exact duplicate(s) '
                         f'also in folder</span>' if rec["dupe_names"] else "")
            tiles.append(
                f'<figure class="t{alt}"><img src="{out_name}" loading="lazy" '
                f'width="{w}" height="{h}" alt="photo {num}">'
                f'<figcaption><b>{num}</b>'
                f'<span class="m">{rec["format"]} &middot; {rec["w"]}&times;{rec["h"]}'
                f' &middot; {rec["bytes"]/1024:.0f} KB</span>{dupe_note}</figcaption></figure>')

    with open(os.path.join(OUTDIR, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)

    fmts = {}
    for rec in manifest:
        fmts[rec["format"]] = fmts.get(rec["format"], 0) + 1
    fmt_line = ", ".join(f"{v} x {k}" for k, v in sorted(fmts.items()))
    multi = sum(1 for g in groups if len(g) > 1)

    sheet = f"""<meta charset="utf-8"><title>Photo contact sheet</title>
<style>
 body{{font:400 15px/1.55 system-ui,sans-serif;margin:0;padding:26px;background:#F1F5F9;color:#2A2E33}}
 h1{{font-size:22px;margin:0 0 4px}}
 .sub{{color:#5b6470;margin-bottom:20px}}
 .grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}}
 .t{{background:#fff;border:1px solid #D9E2ED;margin:0;display:flex;flex-direction:column}}
 .t.alt-of-group{{border-color:#E8B04B;background:#FFFDF6}}
 .t img{{width:100%;height:auto;display:block}}
 figcaption{{padding:9px 11px;display:flex;flex-direction:column;gap:2px}}
 figcaption b{{font-size:15px}}
 .m{{font-size:11.5px;color:#6b7480}}
 .d{{font-size:11.5px;color:#B5732E}}
 .key{{background:#fff;border:1px solid #D9E2ED;padding:14px 16px;margin-bottom:20px}}
</style>
<h1>Contact sheet &mdash; {len(manifest)} photos</h1>
<p class="sub">{len(files)} files in, {exact_dupes} byte-identical duplicates dropped,
   {len(manifest)} kept. Formats: {fmt_line}.
   {multi} group(s) contain near-identical shots.</p>
<div class="key"><b>How to use this:</b> scroll through and write the number plus what it
 shows &mdash; e.g. <i>014 &mdash; Mustang convertible top, finished</i>. Cream-bordered
 tiles are near-identical to the plain tile above them: pick the one you like and ignore
 the rest. Anything you do not label is simply not used.</div>
<div class="grid">{"".join(tiles)}</div>
"""
    with open(os.path.join(OUTDIR, "contact-sheet.html"), "w", encoding="utf-8") as fh:
        fh.write(sheet)

    print(f"files scanned      : {len(files)}")
    print(f"exact duplicates   : {exact_dupes}")
    print(f"unique photos kept : {len(manifest)}")
    print(f"near-identical grps: {multi}")
    print(f"real formats       : {fmt_line}")
    print(f"true HEIC support  : {'yes (pillow-heif)' if HEIF else 'not installed'}")
    if unreadable:
        print(f"\nUNREADABLE ({len(unreadable)}) — these need a look:")
        for name, why in unreadable:
            print(f"   {name}: {why}")
    print(f"\nopen: {os.path.join(OUTDIR, 'contact-sheet.html')}")


if __name__ == "__main__":
    main()
