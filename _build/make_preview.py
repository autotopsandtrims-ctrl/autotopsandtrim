"""Flatten a built page into ONE self-contained file for a shareable mobile
preview: CSS, fonts and images all inlined as data URIs.

    python make_preview.py                     the home page, as before
    python make_preview.py auto-upholstery.html   any other built page
    python make_preview.py auto-upholstery.html --out C:\\path\\to\\file.html

The page argument was added 2026-08-13 to preview the paid LANDING pages, which
carry the site's own <style> block inline on top of site.css — so the flattener
has to keep whatever is already in <head>, not just site.css. See KEEP_HEAD.
"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = REPO
SCRATCH = HERE

args = [a for a in sys.argv[1:] if not a.startswith("--")]
PAGE = args[0] if args else "index.html"

OUTFILE = os.path.join(HERE, "preview.html")
if "--out" in sys.argv:
    OUTFILE = sys.argv[sys.argv.index("--out") + 1]

TIER = "-800.webp"          # good on retina, small enough to inline


def strip_css_comments(text):
    """Remove /* ... */ from CSS before inlining it into the preview.

    Belt and braces, and it roughly halves the inlined CSS. The stylesheets in
    this repo carry very long explanatory comments and two of them contain
    literal HTML tags — site.css warns "NEVER put overflow on <html> or <body>",
    and build_landing's block says "before/after is its own <section> now". Those
    are inert inside a real <style> element (HTML parses style content as
    RAWTEXT; only `</style` ends it) but they are live ammunition for any regex
    that goes looking for tags, which is exactly what this script does.

    See the note above the head/body split for the bug that actually shipped.

    The `[^*]*\\*+(?:[^/*][^*]*\\*+)*` form is the standard non-backtracking C
    comment match, so it cannot blow up on a large stylesheet.
    """
    return re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", text)


def data_uri(path, mime):
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()


with open(os.path.join(REPO, PAGE), encoding="utf-8") as fh:
    html = fh.read()
with open(os.path.join(REPO, "assets", "site.css"), encoding="utf-8") as fh:
    css = fh.read()

# --- inline fonts into the CSS ---
for m in set(re.findall(r"url\((fonts/[^)]+\.woff2)\)", css)):
    uri = data_uri(os.path.join(REPO, "assets", m), "font/woff2")
    css = css.replace(f"url({m})", f"url({uri})")

# --- collect the images this page actually uses, at one tier ---
#
# THE TIER SUFFIX IS MATCHED AS \d+, NOT AS A LIST OF KNOWN WIDTHS.
# This was `-(480|800|1400)` and it silently broke the header logo. The logo is
# `logo-badge-warm-929.webp` — make_responsive.py emits a tier at the source
# image's own width when that width is not one of the standard three, so 929 is
# a perfectly normal filename and simply was not in the list. The stem then
# never reduced to a base, the base never matched, and fix_img() left
# `src="assets/logo-badge-warm-929.webp"` as a relative path that resolves to
# nothing once the file is viewed anywhere but the repo root. The result is a
# broken-image icon where the wordmark should be.
#
# Any hardcoded list of widths here is a latent version of the same bug.
ASSETS = os.path.join(REPO, "assets")
TIER_RE = re.compile(r"-(\d{2,5})\.(?:webp|jpg)$", re.I)


def base_of(ref):
    """'logo-badge-warm-929.webp' -> 'logo-badge-warm'.

    A reference with no tier suffix just loses its extension, so both forms
    collapse to the same key and fix_img() cannot miss one.
    """
    stripped = TIER_RE.sub("", ref)
    if stripped == ref:
        stripped = re.sub(r"\.(?:webp|jpg)$", "", ref, flags=re.I)
    return stripped


def widest(cands):
    """Largest tier NUMERICALLY. Lexicographic sort puts -800 after -1400."""
    def width(f):
        m = TIER_RE.search(f)
        return int(m.group(1)) if m else 0
    return max(cands, key=width)


used = set(re.findall(r'assets/([^"\s]+\.(?:webp|jpg))', html))
bases = {base_of(u) for u in used}

uri_for = {}
unresolved = []
total = 0
for base in sorted(bases):
    cand = os.path.join(ASSETS, base + TIER)
    if not os.path.exists(cand):
        alts = [f for f in os.listdir(ASSETS)
                if f.lower().endswith((".webp", ".jpg")) and base_of(f) == base]
        if not alts:
            unresolved.append(base)
            continue
        cand = os.path.join(ASSETS, widest(alts))
    total += os.path.getsize(cand)
    uri_for[base] = data_uri(cand, "image/webp")


# --- rewrite every src/srcset to the single inlined tier ---
def fix_img(tag):
    m = re.search(r'src="assets/([^"]+)"', tag)
    if not m:
        return tag
    base = base_of(m.group(1))
    if base not in uri_for:
        return tag
    tag = re.sub(r'\ssrcset="[^"]*"', "", tag)
    tag = re.sub(r'\ssizes="[^"]*"', "", tag)
    tag = re.sub(r'src="assets/[^"]+"', f'src="{uri_for[base]}"', tag)
    return tag


html = re.sub(r"<img\b[^>]*>", lambda m: fix_img(m.group(0)), html)

# --- strip document chrome; artifacts supply their own ---
#
# THE BODY IS SEARCHED FOR ONLY AFTER </head>, AND THAT IS NOT FUSSINESS.
# Searching the whole document for `<body[^>]*>` matches the FIRST occurrence,
# and on the landing pages the first occurrence is not the body tag at all — it
# is the words "<body>" inside a CSS comment in the inline stylesheet up in
# <head> ("NEVER put overflow on <html> or <body>"). The extracted "body" then
# began ~6KB early, in the middle of the mobile pass, so the preview opened with
# a wall of raw CSS printed as text above the header. It reads as a broken font
# or a missing stylesheet, which is how it was reported, and neither is what it
# was. Slice the document at </head> first and the ambiguity cannot arise.
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
_head = re.search(r"<head[^>]*>(.*?)</head>", html, re.S)
head_html = _head.group(1)
body = re.search(r"<body[^>]*>(.*)</body>", html[_head.end():], re.S).group(1)

# KEEP_HEAD: the landing pages emit LANDING_CSS as an inline <style> in <head>,
# and every .lp rule lives there rather than in site.css. Dropping the whole
# head — which this script used to do, because the home page has nothing in it
# worth keeping — renders a landing page as unstyled text on a white ground.
KEEP_HEAD = "\n".join(
    "<style>" + strip_css_comments(m.group(1)) + "</style>"
    for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", head_html, re.S))

# nav links point at pages that aren't in this single-file preview
body = re.sub(r'href="(?!tel:|mailto:|#)[^"]*\.html"', 'href="#" data-preview-inert="1"', body)

# The preview is meant to be viewable anywhere, including a sandbox that blocks
# every external request. A Google Maps iframe there is not "a map that failed to
# load", it is a silent empty box that reads as a broken section — so say what it
# is instead. The live page keeps the real embed.
body = re.sub(
    r"<iframe\b[^>]*></iframe>",
    '<div style="display:flex;align-items:center;justify-content:center;'
    'height:100%;min-height:210px;background:#E8EEF6;color:#5A626B;'
    "font:600 13px/1.4 'Archivo',system-ui,sans-serif;text-align:center;"
    'padding:16px">Google map embed<br>(live on the real page)</div>',
    body)

# Never let a preview POST a real lead into Formspree.
body = body.replace('action="https://formspree.io/f/mrpzzdgz"',
                    'action="#" onsubmit="return false"')
body = body.replace('<a class="skip" href="#">', '<a class="skip" href="#main">')

note = f"""
<div style="background:#16344F;color:#fff;padding:11px 16px;text-align:center;
  font:600 13px/1.5 'Archivo',system-ui,sans-serif;">
  Preview &mdash; {PAGE}. Links, the form and the map are inactive here.
</div>
"""

out = (f"<title>{title}</title>\n<style>\n{strip_css_comments(css)}\n</style>\n"
       f"{KEEP_HEAD}\n{note}{body}")
with open(OUTFILE, "w", encoding="utf-8") as fh:
    fh.write(out)

print(f"images inlined : {len(uri_for)}  ({total/1024:.0f} KB raw)")
print(f"preview file   : {os.path.getsize(OUTFILE)/1024/1024:.2f} MB")

# --- SELF-CHECK. A preview that quietly ships a broken image is worse than one
# that refuses to build, because the reader assumes the SITE is broken. The logo
# shipped as a broken-image icon exactly once; this is what makes that loud.
problems = []
if unresolved:
    problems.append("no file on disk for: " + ", ".join(unresolved))

leftover = sorted(set(re.findall(r'(?:src|href)="(assets/[^"]+)"', out)))
if leftover:
    problems.append("relative asset paths left in output (these WILL 404): "
                    + ", ".join(leftover[:8]))

# Only things that FETCH. An <a href> to the shop's Facebook page is a link the
# reader may click, not a resource the page loads, and flagging it would train
# whoever runs this next to ignore the whole self-check.
remote = sorted(set(re.findall(r'\ssrc="(https?://[^"]+)"', out))
                | set(re.findall(r'<link\b[^>]*\shref="(https?://[^"]+)"', out)))
if remote:
    problems.append("external resource loads left in output: " + ", ".join(remote[:5]))

if re.search(r"url\(fonts/", out):
    problems.append("a @font-face is still pointing at a relative path — the "
                    "preview will fall back to a system font and look like the "
                    "typeface was changed")

if problems:
    print("\n*** PREVIEW IS NOT CLEAN ***")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("self-check     : clean (no broken refs, no external requests)")
