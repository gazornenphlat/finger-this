import hashlib, json, os, shutil, zipfile
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist", "finger-this")
shutil.rmtree(os.path.join(ROOT, "dist"), ignore_errors=True)
os.makedirs(os.path.join(DIST, "icons"))
body = open(os.path.join(ROOT, "src", "app.html"), encoding="utf-8").read()

# ---- icons: rosewood neck with a brass note on it ----
def icon(size, maskable=False):
    im = Image.new("RGBA", (size, size), (21, 17, 14, 255))
    d = ImageDraw.Draw(im)
    pad = int(size * (0.2 if maskable else 0.1))
    x0, y0, x1, y1 = pad, int(size * 0.28), size - pad, int(size * 0.72)
    d.rounded_rectangle((x0, y0, x1, y1), radius=size // 30, fill=(75, 45, 31))
    for k in range(1, 4):
        x = x0 + (x1 - x0) * k / 4
        d.line((x, y0, x, y1), fill=(185, 180, 171), width=max(2, size // 70))
    for k in range(4):
        y = y0 + (y1 - y0) * (k + 0.5) / 4
        d.line((x0, y, x1, y), fill=(239, 229, 211), width=max(1, size // 120 + k // 2))
    d.rectangle((x0 - size // 60, y0, x0, y1), fill=(239, 229, 211))
    cx, cy, r = x0 + (x1 - x0) * 0.625, y0 + (y1 - y0) * 0.625, size * 0.085
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(216, 169, 76))
    return im

for s in (192, 512):
    icon(s).save(os.path.join(DIST, "icons", f"icon-{s}.png"))
icon(512, True).save(os.path.join(DIST, "icons", "maskable-512.png"))
icon(256).save(os.path.join(DIST, "icons", "favicon.ico"), sizes=[(32, 32), (64, 64)])

manifest = {
    "name": "Finger This – Scales, Tuner & Metronome",
    "short_name": "Finger This",
    "description": "Learn scales on guitar, banjo and ukulele with a tuner and metronome.",
    "start_url": "./index.html",
    "scope": "./",
    "display": "fullscreen",
    "display_override": ["fullscreen", "standalone"],
    "orientation": "landscape",
    "background_color": "#15110e",
    "theme_color": "#15110e",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
json.dump(manifest, open(os.path.join(DIST, "manifest.webmanifest"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

sw_ver = hashlib.sha256(body.encode('utf-8')).hexdigest()[:8]
sw = """const C='finger-this-""" + sw_ver + """';
const SHELL=['./','./index.html','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/maskable-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{
    const copy=r.clone();caches.open(C).then(c=>c.put(e.request,copy)).catch(()=>{});return r;}).catch(()=>hit)));
});
"""
open(os.path.join(DIST, "sw.js"), "w").write(sw)

head = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#15110e">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon.ico">
<link rel="apple-touch-icon" href="icons/icon-192.png">
<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style>
<script>window.__PWA=true</script>
</head><body>
"""
open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(head + body + "\n</body></html>\n")

readme = open(os.path.join(ROOT, "src", "INSTALL.txt"), encoding="utf-8").read()
open(os.path.join(DIST, "INSTALL.txt"), "w", encoding="utf-8").write(readme)

# preview copy for the hosted artifact (skeleton is added by the host)
open(os.path.join(ROOT, "dist", "preview.html"), "w", encoding="utf-8").write(body)

z = os.path.join(ROOT, "dist", "FingerThis-app.zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for base, _, files in os.walk(DIST):
        for f in files:
            p = os.path.join(base, f)
            zf.write(p, os.path.join("finger-this", os.path.relpath(p, DIST)))
print("built", z)
