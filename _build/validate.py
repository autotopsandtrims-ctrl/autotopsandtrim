"""Verify every internal link, image src, srcset entry and stylesheet resolves."""
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = REPO
SCRATCH = HERE


htmls = sorted(f for f in os.listdir(REPO) if f.endswith(".html"))
missing, ok_refs = [], 0
sizes = {}

for name in htmls:
    path = os.path.join(REPO, name)
    sizes[name] = os.path.getsize(path)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()

    refs = set()
    refs |= set(re.findall(r'href="([^"#:]+\.(?:html|css|xml|txt))"', src))
    refs |= set(re.findall(r'src="([^"]+)"', src))
    for ss in re.findall(r'srcset="([^"]+)"', src):
        for part in ss.split(","):
            part = part.strip().split(" ")[0]
            if part:
                refs.add(part)

    for ref in refs:
        if ref.startswith(("http", "tel:", "mailto:", "data:")):
            continue
        target = os.path.join(REPO, ref.replace("/", os.sep))
        if os.path.exists(target):
            ok_refs += 1
        else:
            missing.append((name, ref))

print(f"pages checked   : {len(htmls)}")
print(f"refs resolved   : {ok_refs}")
print(f"refs MISSING    : {len(missing)}")
for n, r in missing[:25]:
    print(f"   {n} -> {r}")

# unclosed-tag smoke test on the biggest structural elements
print("\n--- tag balance ---")
for name in htmls:
    with open(os.path.join(REPO, name), encoding="utf-8") as fh:
        s = fh.read()
    for tag in ("div", "section", "a", "ul", "figure"):
        o = len(re.findall(rf"<{tag}[\s>]", s))
        c = len(re.findall(rf"</{tag}>", s))
        if o != c:
            print(f"  {name}: <{tag}> {o} open / {c} close")

print("\n--- page sizes (HTML only) ---")
for n, s in sorted(sizes.items(), key=lambda kv: -kv[1])[:6]:
    print(f"  {s/1024:7.1f} KB  {n}")
tot = sum(sizes.values())
print(f"  total HTML: {tot/1024:.1f} KB across {len(htmls)} pages")

# image weight actually pulled by the home page at mobile width
with open(os.path.join(REPO, "index.html"), encoding="utf-8") as fh:
    home = fh.read()
mob = re.findall(r'assets/([^" ]+-480\.webp)', home)
w = sum(os.path.getsize(os.path.join(REPO, "assets", f)) for f in set(mob))
print(f"\nhome page, mobile tier: {len(set(mob))} images, {w/1024:.0f} KB")
