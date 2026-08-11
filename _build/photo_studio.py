"""A local drag-and-drop photo studio. Shopify-ish, but for this static site.

Run it, open the page, drag a photo onto the one you want replaced, watch it
change. Hit Publish when you like it.

    python _build\\photo_studio.py          then open http://localhost:8732

WHY A LOCAL SERVER AND NOT A REAL CMS
Vercel serves committed HTML here — there is no cloud build. Responsive
variants, images.json and every page referencing a photo are all generated
locally, so the editing has to happen where the build lives. This is that,
with a UI on top.

The site itself stays ZERO-JAVASCRIPT. The studio's JS lives only in the
studio page, which is never written to disk and never committed. The pages it
previews are the real built files, byte for byte what goes live.
"""
import io
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ORIGINALS = os.path.join(REPO, "assets", "originals")
ASSETS = os.path.join(REPO, "assets")
CATALOG = os.path.join(HERE, "images.json")
PORT = 8732

WIDTHS = [480, 800, 1400]
QUALITY = 80
EXTS = (".jpg", ".jpeg", ".png", ".webp")
GIT = r"C:\Users\table\AppData\Local\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe"

PAGES = [
    ("convertible-tops", "Convertible Tops"),
    ("auto-upholstery", "Auto Upholstery &amp; Interiors"),
    ("sunroof-shade-repair", "Sunroof Repair"),
    ("headliner-replacement", "Headliner Replacement"),
    ("vinyl-tops", "Vinyl Tops"),
    ("before-after", "Before &amp; After (sitelink)"),
    ("index", "Home"),
]

_lock = threading.Lock()


def page_photos(page):
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


def build_variants(master_path, base):
    with Image.open(master_path) as im:
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


def rebuild():
    """Rebuild and gate. Returns (ok, message)."""
    for script in ("build_pages.py", "validate.py", "dupcheck.py"):
        p = subprocess.run([sys.executable, os.path.join("_build", script)],
                           cwd=REPO, capture_output=True, text=True)
        out = (p.stdout or "") + (p.stderr or "")
        if p.returncode != 0:
            return False, "%s failed: %s" % (script, out[-300:])
        if script == "dupcheck.py":
            m = re.search(r"pages repeating a photo: (\d+)", out)
            if m and m.group(1) != "0":
                return False, "A page now shows the same photo twice. Not saved as final."
        if script == "validate.py":
            m = re.search(r"refs MISSING\s*:\s*(\d+)", out)
            if m and m.group(1) != "0":
                return False, "Broken image reference after rebuild."
    return True, "Rebuilt and checked."


def replace_photo(target, filename, data):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in EXTS:
        return False, "Not an image: %s" % filename
    with _lock:
        for other in EXTS:                      # drop any stale other-extension master
            p = os.path.join(ORIGINALS, target + other)
            if other != ext and os.path.exists(p):
                os.remove(p)
        master = os.path.join(ORIGINALS, target + ext)
        with open(master, "wb") as fh:
            fh.write(data)
        try:
            with open(CATALOG, encoding="utf-8") as fh:
                cat = json.load(fh)
            cat[target] = build_variants(master, target)
            with open(CATALOG, "w", encoding="utf-8") as fh:
                json.dump(cat, fh, indent=1)
        except Exception as e:                  # noqa: BLE001
            return False, "Could not process image: %s" % e
        return rebuild()


def git(*args):
    p = subprocess.run([GIT] + list(args), cwd=REPO, capture_output=True, text=True)
    out = ((p.stdout or "") + (p.stderr or ""))
    return p.returncode, re.sub(r"github_pat_[A-Za-z0-9_]+", "***", out)


STUDIO_CSS = """
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  background:#0f1720;color:#e8eef5}
header{position:sticky;top:0;z-index:9;background:#16344F;padding:14px 20px;
  display:flex;align-items:center;gap:16px;box-shadow:0 6px 20px rgba(0,0,0,.4)}
header h1{margin:0;font-size:17px;font-weight:800;letter-spacing:-.02em}
header .sp{flex:1}
button{font:inherit;font-weight:700;border:0;border-radius:9px;padding:10px 16px;
  cursor:pointer;background:#2F6FB0;color:#fff}
button.ghost{background:transparent;color:#cfe0f0;border:1px solid #3d5f82}
button:disabled{opacity:.5;cursor:default}
#status{padding:10px 20px;font-size:13.5px;background:#132434;border-bottom:1px solid #24384c;
  position:sticky;top:56px;z-index:8}
#status.err{background:#4a1d1d;color:#ffd8d8}
#status.ok{background:#14361f;color:#d3f5df}
.wrap{padding:18px 20px 60px;max-width:1500px;margin:0 auto}
h2{font-size:15px;margin:26px 0 10px;color:#9fc0e0;letter-spacing:.04em;text-transform:uppercase}
h2 a{color:#6fa8dd;font-size:12px;margin-left:10px;text-transform:none;letter-spacing:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px}
.card{background:#182634;border:1px solid #24384c;border-radius:12px;overflow:hidden;
  position:relative;transition:border-color .15s,transform .15s}
.card.over{border-color:#5E9BD9;transform:scale(1.02)}
.card.busy{opacity:.5}
.card .ph{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#0b1219}
.card .meta{padding:8px 10px}
.card .n{font-weight:800;font-size:12px;color:#7fb0e2}
.card .nm{font-size:11px;color:#8fa5ba;word-break:break-all;line-height:1.35}
.card .hint{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  background:rgba(11,18,25,.86);color:#cfe4ff;font-weight:700;font-size:13px;opacity:0;
  transition:opacity .15s;pointer-events:none;text-align:center;padding:12px}
.card.over .hint{opacity:1}
"""

STUDIO_JS = """
function setStatus(msg, kind){
  var s=document.getElementById('status');
  s.textContent=msg; s.className=kind||'';
}
function bust(img){
  var u=img.getAttribute('data-src');
  img.src=u+'?t='+Date.now();
}
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.card').forEach(function(card){
    ['dragenter','dragover'].forEach(function(e){
      card.addEventListener(e,function(ev){ev.preventDefault();card.classList.add('over');});
    });
    ['dragleave','drop'].forEach(function(e){
      card.addEventListener(e,function(ev){ev.preventDefault();card.classList.remove('over');});
    });
    card.addEventListener('drop',function(ev){
      var f=ev.dataTransfer.files[0]; if(!f) return;
      var target=card.getAttribute('data-target');
      card.classList.add('busy');
      setStatus('Processing '+f.name+' -> '+target+' ...');
      f.arrayBuffer().then(function(buf){
        return fetch('/api/replace?target='+encodeURIComponent(target)+
                     '&filename='+encodeURIComponent(f.name),
                     {method:'POST',body:buf});
      }).then(function(r){return r.json();}).then(function(j){
        card.classList.remove('busy');
        if(j.ok){
          document.querySelectorAll('img[data-target="'+target+'"]').forEach(bust);
          setStatus(target+' updated. '+j.msg+'  (not live until you Publish)','ok');
        } else { setStatus('FAILED: '+j.msg,'err'); }
      }).catch(function(e){
        card.classList.remove('busy'); setStatus('FAILED: '+e,'err');
      });
    });
  });
  document.getElementById('publish').addEventListener('click',function(){
    if(!confirm('Publish all photo changes to the live website?')) return;
    this.disabled=true; setStatus('Publishing ...');
    fetch('/api/publish',{method:'POST'}).then(function(r){return r.json();})
     .then(function(j){
       document.getElementById('publish').disabled=false;
       setStatus(j.ok?('PUBLISHED. '+j.msg):('FAILED: '+j.msg), j.ok?'ok':'err');
     });
  });
  document.getElementById('reload').addEventListener('click',function(){location.reload();});
});
"""


def studio_html():
    rows = []
    for slug, label in PAGES:
        photos = page_photos(slug)
        if not photos:
            continue
        cards = []
        for i, base in enumerate(photos, 1):
            thumb = "/assets/%s-480.webp" % base
            if not os.path.exists(os.path.join(ASSETS, "%s-480.webp" % base)):
                cand = [f for f in os.listdir(ASSETS)
                        if f.startswith(base + "-") and f.endswith(".webp")]
                thumb = "/assets/" + cand[0] if cand else ""
            cards.append(
                '<div class="card" data-target="{b}">'
                '<img class="ph" data-target="{b}" data-src="{t}" src="{t}" alt="">'
                '<div class="hint">Drop to replace<br>#{i}</div>'
                '<div class="meta"><div class="n">#{i}</div>'
                '<div class="nm">{b}</div></div></div>'.format(b=base, t=thumb, i=i))
        rows.append(
            '<h2>{lab} <a href="/{slug}.html" target="_blank">open the real page &rarr;</a></h2>'
            '<div class="grid">{cards}</div>'.format(
                lab=label, slug=slug, cards="".join(cards)))
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Photo Studio &middot; Auto Tops and Trim</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>%s</style></head><body>
<header><h1>Photo Studio</h1>
  <span class="sp"></span>
  <button class="ghost" id="reload">Refresh list</button>
  <button id="publish">Publish live</button>
</header>
<div id="status">Drag a photo from your computer onto any tile to replace it.
  Nothing goes live until you press Publish.</div>
<div class="wrap">%s</div>
<script>%s</script></body></html>""" % (STUDIO_CSS, "".join(rows), STUDIO_JS)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=REPO, **kw)

    def log_message(self, *a):
        pass

    def _json(self, ok, msg):
        body = json.dumps({"ok": ok, "msg": msg}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index", "/studio"):
            body = studio_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/api/replace":
            target = (qs.get("target") or [""])[0]
            filename = (qs.get("filename") or ["drop.jpg"])[0]
            n = int(self.headers.get("Content-Length") or 0)
            data = self.rfile.read(n)
            if not target or not data:
                return self._json(False, "missing target or file")
            ok, msg = replace_photo(target, filename, data)
            return self._json(ok, msg)
        if parsed.path == "/api/publish":
            git("add", "-A")
            rc, out = git("-c", "user.name=photo-studio",
                          "-c", "user.email=noreply@autotopsandtrim.com",
                          "commit", "-m", "Update photos via photo studio")
            if "nothing to commit" in out:
                return self._json(False, "No changes to publish.")
            rc, out = git("push", "origin", "HEAD")
            if rc != 0:
                return self._json(False, out[-300:])
            return self._json(True, "Live in about a minute.")
        return self._json(False, "unknown endpoint")


if __name__ == "__main__":
    print("=" * 62)
    print("  PHOTO STUDIO")
    print("=" * 62)
    print("  Open:  http://localhost:%d" % PORT)
    print("  Drag a photo onto any tile to replace it.")
    print("  Nothing goes live until you press Publish.")
    print("  Ctrl+C here to stop.")
    print("=" * 62)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
