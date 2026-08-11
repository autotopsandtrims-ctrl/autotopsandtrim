"""Drag-and-drop photo updater. Drop images in photo-drop/, run this, done.

WHY THIS EXISTS
Vercel serves committed HTML for this site — there is no build step in the
cloud. So dropping a JPG into GitHub does nothing: the responsive variants, the
images.json catalog and every page that references the photo are all generated
here. This script is that whole loop in one command.

HOW TO NAME A DROPPED FILE — three ways, easiest first:

  1. PAGE + SLOT      convertible-tops-6.jpg
     Replaces the 6th photo on the convertible-tops page, using the numbering
     this script prints when you run it with --list. Nothing to look up.

  2. EXACT BASENAME   shot-087-old-black-top-faded.jpg
     Replaces that photo EVERYWHERE it appears, on every page at once.

  3. ANYTHING ELSE    my-new-shot.jpg
     Imported and catalogued, but NOT shown anywhere yet — a photo has to be
     placed into a page's config to appear. The script says so rather than
     silently doing nothing.

    python _build\\photo_drop.py --list     show every page's photos, numbered
    python _build\\photo_drop.py            process the drop folder (no push)
    python _build\\photo_drop.py --push     process, then commit and push live
"""
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DROP = os.path.join(REPO, "photo-drop")
ORIGINALS = os.path.join(REPO, "assets", "originals")
ASSETS = os.path.join(REPO, "assets")
CATALOG = os.path.join(HERE, "images.json")

# 1400 is the widest tier anything on this site is displayed at. The pipeline
# used to also emit a native-width variant, which for a modern phone photo meant
# a 4000px WebP of about 800KB that no layout ever requested.
WIDTHS = [480, 800, 1400]
QUALITY = 80
EXTS = (".jpg", ".jpeg", ".png", ".webp")

LANDING = ["convertible-tops", "auto-upholstery", "headliner-replacement",
           "sunroof-shade-repair", "vinyl-tops", "before-after", "contact",
           "index", "gallery"]

GIT = r"C:\Users\table\AppData\Local\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe"


def page_photos(page):
    """Photo basenames on a built page, in the order a visitor meets them."""
    path = os.path.join(REPO, page + ".html")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        body = fh.read().split("</main>")[0]
    seen, out = set(), []
    for m in re.finditer(r'src="assets/([a-z0-9\-]+?)-\d+\.webp"', body):
        n = m.group(1)
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def show_list():
    for page in LANDING:
        photos = page_photos(page)
        if not photos:
            continue
        print("\n%s   (drop a file named %s-N.jpg to replace one)" % (page, page))
        for i, n in enumerate(photos, 1):
            print("  %2d. %s" % (i, n))


def resolve(filename):
    """Work out which existing photo a dropped file is meant to replace."""
    base = os.path.splitext(os.path.basename(filename))[0]
    # form 1: page + slot number
    m = re.match(r"^(.*?)-(\d+)$", base)
    if m and m.group(1) in LANDING:
        page, idx = m.group(1), int(m.group(2))
        photos = page_photos(page)
        if 1 <= idx <= len(photos):
            return photos[idx - 1], "replaces #%d on %s" % (idx, page)
        return None, "page %s has only %d photos, no #%d" % (page, len(photos), idx)
    # form 2: exact existing basename
    for ext in EXTS:
        if os.path.exists(os.path.join(ORIGINALS, base + ext)):
            return base, "replaces %s everywhere it appears" % base
    # form 3: brand new
    return base, "NEW photo — imported, but not shown on any page yet"


def build_variants(master_path, base):
    with Image.open(master_path) as im:
        has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
        im = im.convert("RGBA" if has_alpha else "RGB")
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
        if not variants:                       # source narrower than 480
            fn = "%s-%d.webp" % (base, ow)
            im.save(os.path.join(ASSETS, fn), "WEBP", quality=QUALITY, method=6)
            variants.append({"w": ow, "h": oh, "file": fn})
    return {"w": ow, "h": oh, "variants": variants}


def run(cmd, cwd=REPO):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=False)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    if "--list" in sys.argv:
        show_list()
        return 0

    os.makedirs(DROP, exist_ok=True)
    files = [f for f in sorted(os.listdir(DROP)) if f.lower().endswith(EXTS)]
    if not files:
        print("Nothing in photo-drop/.")
        print("Put images there, then run this again.")
        print("Name them like  convertible-tops-6.jpg  to replace photo #6 on that page.")
        print("Run with --list to see every page's photos numbered.")
        return 0

    with open(CATALOG, encoding="utf-8") as fh:
        cat = json.load(fh)

    print("=" * 70)
    print("PROCESSING %d FILE(S)" % len(files))
    print("=" * 70)
    done, new_only = [], []
    for f in files:
        src = os.path.join(DROP, f)
        target, why = resolve(f)
        if target is None:
            print("  SKIP  %-28s %s" % (f, why))
            continue
        ext = os.path.splitext(f)[1].lower()
        master = os.path.join(ORIGINALS, target + ext)
        # Remove any other-extension master for the same basename, or the site
        # would keep two masters and the next full run could pick the stale one.
        for other in EXTS:
            p = os.path.join(ORIGINALS, target + other)
            if other != ext and os.path.exists(p):
                os.remove(p)
        shutil.copy2(src, master)
        cat[target] = build_variants(master, target)
        print("  OK    %-28s -> %-34s %s" % (f, target, why))
        done.append(target)
        if why.startswith("NEW"):
            new_only.append(target)
        os.remove(src)

    if not done:
        print("\nNothing processed.")
        return 1

    with open(CATALOG, "w", encoding="utf-8") as fh:
        json.dump(cat, fh, indent=1)

    print("\n" + "=" * 70)
    print("REBUILDING SITE")
    print("=" * 70)
    for script, label in ((("build_pages.py"), "build"),
                          (("validate.py"), "validate"),
                          (("dupcheck.py"), "dupcheck")):
        rc, out = run([sys.executable, os.path.join("_build", script)])
        tail = [l for l in out.splitlines() if l.strip()][-3:]
        for l in tail:
            print("  %s" % l)
        if rc != 0:
            print("\nGATE FAILED (%s). Nothing pushed. Fix it and run again." % label)
            return 1

    if new_only:
        print("\n" + "!" * 70)
        print("These were imported but appear NOWHERE yet — a photo has to be")
        print("placed into a page before it shows:")
        for n in new_only:
            print("   %s" % n)
        print("!" * 70)

    if "--push" not in sys.argv:
        print("\nDone locally. Nothing pushed.")
        print("Re-run with --push to put it live.")
        return 0

    print("\n" + "=" * 70)
    print("PUSHING LIVE")
    print("=" * 70)
    run([GIT, "add", "-A"])
    msg = "Update photos: " + ", ".join(done[:6]) + ("..." if len(done) > 6 else "")
    rc, out = run([GIT, "-c", "user.name=photo-drop",
                   "-c", "user.email=noreply@autotopsandtrim.com",
                   "commit", "-m", msg])
    print("  " + (out.strip().splitlines() or ["nothing to commit"])[0])
    rc, out = run([GIT, "push", "origin", "HEAD"])
    out = re.sub(r"github_pat_[A-Za-z0-9_]+", "***", out)
    for l in out.strip().splitlines()[-2:]:
        print("  %s" % l)
    print("\nLIVE in about a minute at https://www.autotopsandtrim.com")
    return 0


if __name__ == "__main__":
    sys.exit(main())
