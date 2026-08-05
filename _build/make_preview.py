"""Flatten the built home page into ONE self-contained file for a shareable
mobile preview: CSS, fonts and images all inlined as data URIs."""
import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = REPO
SCRATCH = HERE


OUTFILE = os.path.join(HERE, "preview.html")

PAGE = "index.html"
TIER = "-800.webp"          # good on retina, small enough to inline


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
used = set(re.findall(r'assets/([^"\s]+\.(?:webp|jpg))', html))
bases = {re.sub(r"-(480|800|1400)\.webp$", "", u) for u in used}

uri_for = {}
total = 0
for base in bases:
    cand = os.path.join(REPO, "assets", base + TIER)
    if not os.path.exists(cand):
        alts = [f for f in os.listdir(os.path.join(REPO, "assets"))
                if f.startswith(base + "-") and f.endswith(".webp")]
        if not alts:
            continue
        cand = os.path.join(REPO, "assets", sorted(alts)[-1])
    total += os.path.getsize(cand)
    uri_for[base] = data_uri(cand, "image/webp")

# --- rewrite every src/srcset to the single inlined tier ---
def fix_img(tag):
    m = re.search(r'src="assets/([^"]+)"', tag)
    if not m:
        return tag
    base = re.sub(r"-(480|800|1400)\.webp$", "", m.group(1))
    base = re.sub(r"\.(webp|jpg)$", "", base)
    if base not in uri_for:
        return tag
    tag = re.sub(r'\ssrcset="[^"]*"', "", tag)
    tag = re.sub(r'\ssizes="[^"]*"', "", tag)
    tag = re.sub(r'src="assets/[^"]+"', f'src="{uri_for[base]}"', tag)
    return tag


html = re.sub(r"<img\b[^>]*>", lambda m: fix_img(m.group(0)), html)

# --- strip document chrome; artifacts supply their own ---
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
body = re.search(r"<body[^>]*>(.*)</body>", html, re.S).group(1)

# nav links point at pages that aren't in this single-file preview
body = re.sub(r'href="(?!tel:|mailto:|#)[^"]*\.html"', 'href="#" data-preview-inert="1"', body)
body = body.replace('<a class="skip" href="#">', '<a class="skip" href="#main">')

note = """
<div style="background:#16344F;color:#fff;padding:11px 16px;text-align:center;
  font:600 13px/1.5 'Archivo',system-ui,sans-serif;">
  Mobile preview &mdash; home page only. Links are inactive here; the full 15-page site is on the rebuild branch.
</div>
"""

out = f"<title>{title}</title>\n<style>\n{css}\n</style>\n{note}{body}"
with open(OUTFILE, "w", encoding="utf-8") as fh:
    fh.write(out)

print(f"images inlined : {len(uri_for)}  ({total/1024:.0f} KB raw)")
print(f"preview file   : {os.path.getsize(OUTFILE)/1024/1024:.2f} MB")
