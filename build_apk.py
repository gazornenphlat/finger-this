"""Builds dist/FingerThis.apk from the web app (run build.py first)."""
import os, re, shutil, subprocess
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
AND = os.path.join(ROOT, "android")
OUT = os.path.join(ROOT, "build-apk")
JAR = "/usr/lib/android-sdk/platforms/android-23/android.jar"
KS = os.path.join(ROOT, "signing", "finger-this.jks")
# Signing password: never hardcode it. Set FINGERTHIS_KS_PASS, or put the
# password on one line in signing/password.txt (gitignored, like the .jks).
PW = os.environ.get("FINGERTHIS_KS_PASS", "").strip()
if not PW:
    _pw_file = os.path.join(ROOT, "signing", "password.txt")
    if os.path.exists(_pw_file):
        with open(_pw_file, encoding="utf-8") as _f:
            PW = _f.read().strip()

def run(*cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        raise SystemExit(f"FAILED: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r.stdout

shutil.rmtree(OUT, ignore_errors=True)
for d in ("obj", "assets", "res"):
    os.makedirs(os.path.join(OUT, d))
shutil.copytree(os.path.join(AND, "res"), os.path.join(OUT, "res"), dirs_exist_ok=True)

# launcher icons from the app icon
src = Image.open(os.path.join(ROOT, "dist", "finger-this", "icons", "icon-512.png"))
for name, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    d = os.path.join(OUT, "res", f"mipmap-{name}")
    os.makedirs(d, exist_ok=True)
    src.resize((px, px), Image.LANCZOS).save(os.path.join(d, "ic_launcher.png"))

# the app page, without the web-install extras (manifest, service worker)
html = open(os.path.join(ROOT, "dist", "finger-this", "index.html"), encoding="utf-8").read()
html = html.replace("<script>window.__PWA=true</script>\n", "")
html = re.sub(r'<link rel="(manifest|icon|apple-touch-icon)"[^>]*>\n', "", html)
open(os.path.join(OUT, "assets", "index.html"), "w", encoding="utf-8").write(html)

# compile -> dex -> package -> align -> sign
srcs = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(AND, "src")) for f in fs if f.endswith(".java")]
run("javac", "-nowarn", "-source", "8", "-target", "8", "-bootclasspath", JAR, "-classpath", JAR,
    "-d", os.path.join(OUT, "obj"), *srcs)
run("dalvik-exchange", "--dex", "--min-sdk-version=24", f"--output={os.path.join(OUT, 'classes.dex')}", os.path.join(OUT, "obj"))
unsigned = os.path.join(OUT, "unsigned.apk")
run("aapt", "package", "-f", "-M", os.path.join(AND, "AndroidManifest.xml"), "-S", os.path.join(OUT, "res"),
    "-A", os.path.join(OUT, "assets"), "-I", JAR, "-F", unsigned)
run("aapt", "add", "unsigned.apk", "classes.dex", cwd=OUT)
aligned = os.path.join(OUT, "aligned.apk")
run("zipalign", "-f", "-p", "4", unsigned, aligned)

if not os.path.exists(KS):
    raise SystemExit(f"Signing key not found: {KS}\n"
                     "Updates must be signed with the owner's key (finger-this.jks). "
                     "Attach the key you were given; do not generate a new one.")
if not PW:
    raise SystemExit("No signing password: set FINGERTHIS_KS_PASS, or create "
                     "signing/password.txt (one line, in the gitignored signing/ "
                     "folder next to finger-this.jks).")
apk = os.path.join(ROOT, "dist", "FingerThis.apk")
run("apksigner", "sign", "--ks", KS, "--ks-pass", f"pass:{PW}", "--key-pass", f"pass:{PW}",
    "--ks-key-alias", "fingerthis", "--out", apk, aligned)
print(run("apksigner", "verify", "--verbose", apk).splitlines()[:4])
print("built", apk, os.path.getsize(apk), "bytes")
