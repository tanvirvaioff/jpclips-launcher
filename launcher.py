#!/usr/bin/env python3
"""JpClips PC Launcher - part 1: config, logging, download."""

import os
import sys
import time
import shutil
import zipfile
import subprocess
import threading
import traceback
import urllib.request
import urllib.error

APP_TITLE = "JpClips"
PORT = 8000

def _exe_dir():
    """Directory holding the exe (portable mode)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = os.path.join(_exe_dir(), "JpClipsData")
PYTHON_DIR = os.path.join(BASE_DIR, "python")
PYTHON_EXE = os.path.join(PYTHON_DIR, "python.exe")
PYTHONW_EXE = os.path.join(PYTHON_DIR, "pythonw.exe")
APP_DIR = os.path.join(BASE_DIR, "jpclips-pc")
MARKER = os.path.join(BASE_DIR, ".setup_done")
VERSION_FILE = os.path.join(BASE_DIR, "app_version.txt")
LOG_FILE = os.path.join(BASE_DIR, "jpclips_log.txt")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

PYTHON_VERSION = "3.11.9"
PYTHON_EMBED_URL = (
    "https://www.python.org/ftp/python/%s/python-%s-embed-amd64.zip"
    % (PYTHON_VERSION, PYTHON_VERSION))
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

APP_VERSION = "1"

# Embedded setup-window logo (JpClips icon, base64 PNG).
LOGO_DATA_URI = "data:image/png;base64,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"
APP_VERSION_URL = ("https://raw.githubusercontent.com/tanvirvaioff/"
                   "jpclips-launcher/main/app_version.txt")
APP_ZIP_URL = ("https://raw.githubusercontent.com/tanvirvaioff/"
               "jpclips-launcher/main/app/jpclips-pc.zip?v=3")

TORCH_INDEX = "https://download.pytorch.org/whl/cu121"
CHUNK = 1024 * 256


def log(msg):
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as f:
            f.write("[%s] %s\n" % (ts, msg))
    except Exception:
        pass


def download(url, dest, progress_cb=None):
    """Download url -> dest with resume. progress_cb(done_bytes, total_bytes)."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    done = os.path.getsize(part) if os.path.exists(part) else 0

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "JpClips-Launcher/1.0")
    if done > 0:
        req.add_header("Range", "bytes=%d-" % done)

    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 416:
            os.replace(part, dest)
            if progress_cb:
                progress_cb(1, 1)
            return dest
        raise

    total = None
    cr = resp.headers.get("Content-Range")
    if cr and "/" in cr:
        try:
            total = int(cr.rsplit("/", 1)[1])
        except ValueError:
            total = None
    if total is None:
        clen = resp.headers.get("Content-Length")
        if clen:
            try:
                total = int(clen) + done
            except ValueError:
                total = None

    mode = "ab" if done > 0 and resp.status == 206 else "wb"
    if mode == "wb":
        done = 0
    with open(part, mode) as f:
        while True:
            buf = resp.read(CHUNK)
            if not buf:
                break
            f.write(buf)
            done += len(buf)
            if progress_cb:
                progress_cb(done, total or 0)
    os.replace(part, dest)
    if progress_cb:
        progress_cb(total or done, total or done)
    return dest


def fmt_mb(n):
    return "%.1f MB" % (n / 1048576.0)


# ------------------------------------------------------- setup window HTML

SETUP_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f1115;color:#e8eaf0;font-family:'Segoe UI',Arial,sans-serif;
display:flex;align-items:center;justify-content:center;height:100vh}
.card{width:520px;background:#171a21;border:1px solid #262b36;border-radius:16px;
padding:40px 44px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.logoimg{width:96px;height:96px;margin:0 auto 10px;display:block;filter:drop-shadow(0 8px 24px rgba(229,72,77,.35))}
.logo{font-size:42px;font-weight:800;letter-spacing:-1px}
.logo span{color:#e5484d}
.sub{color:#9aa3b2;margin:8px 0 28px;font-size:14px}
.bar{height:10px;background:#262b36;border-radius:6px;overflow:hidden;margin:18px 0 10px}
.fill{height:100%;width:0%;border-radius:6px;
background:linear-gradient(90deg,#e5484d,#f76b15);transition:width .25s}
.steprow{display:flex;justify-content:space-between;align-items:baseline;margin-top:2px}
.step{font-size:14px;color:#e8eaf0;min-height:22px;text-align:left}
.pct{font-size:14px;font-weight:700;color:#f76b15;min-width:52px;text-align:right}
.detail{font-size:12px;color:#9aa3b2;margin-top:6px;min-height:18px}
.indet .fill{width:40%!important;animation:slide 1.2s infinite linear}
@keyframes slide{0%{margin-left:-40%}100%{margin-left:100%}}
.err{color:#ff8585;font-size:13px;margin-top:14px;white-space:pre-wrap;text-align:left;
max-height:180px;overflow:auto}
.note{font-size:11px;color:#6b7280;margin-top:22px}
</style></head>
<body><div class="card">
<img class="logoimg" src="__LOGO_DATA_URI__">
<div class="logo">Jp<span>Clips</span></div>
<div class="sub">First-time setup — downloading what the app needs.<br>One time only, then it just opens.</div>
<div class="bar" id="bar"><div class="fill" id="fill"></div></div>
<div class="steprow"><div class="step" id="step">Starting...</div><div class="pct" id="pct">0%</div></div>
<div class="detail" id="detail"></div>
<div class="err" id="err"></div>
<div class="note">Downloads resume automatically if interrupted.<br>
Nothing is installed into your system Python — everything stays in the JpClipsData folder next to JpClipsPC.exe.</div>
</div>
<script>
function setStep(t){document.getElementById('step').textContent=t;}
function setDetail(t){document.getElementById('detail').textContent=t;}
function setProgress(pct,detail){
  document.getElementById('bar').classList.remove('indet');
  document.getElementById('fill').style.width=pct+'%';
  document.getElementById('pct').textContent=Math.round(pct)+'%';
  if(detail!==undefined)setDetail(detail);
}
function setIndeterminate(){document.getElementById('bar').classList.add('indet');}
function setError(t){document.getElementById('err').textContent=t;}
</script></body></html>"""




# ------------------------------------------------------- splash screen HTML

SPLASH_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f1115;color:#e8eaf0;font-family:'Segoe UI',Arial,sans-serif;
display:flex;align-items:center;justify-content:center;height:100vh}
.wrap{text-align:center}
.logoimg{width:96px;height:96px;margin:0 auto 14px;display:block;
filter:drop-shadow(0 8px 24px rgba(229,72,77,.35))}
h2{font-size:22px;font-weight:600;letter-spacing:.3px}
.spinner{width:44px;height:44px;margin:26px auto 0;border:4px solid #262b36;
border-top-color:#e5484d;border-radius:50%;animation:spin .9s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.dots::after{content:'';animation:dots 1.4s steps(4) infinite}
@keyframes dots{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}}
</style></head>
<body><div class="wrap">
<img class="logoimg" src="__LOGO_DATA_URI__">
<h2>Starting JpClips<span class="dots"></span></h2>
<div class="spinner"></div>
</div></body></html>"""


SETUP_HTML = SETUP_HTML.replace("__LOGO_DATA_URI__", LOGO_DATA_URI)
SPLASH_HTML = SPLASH_HTML.replace("__LOGO_DATA_URI__", LOGO_DATA_URI)
class SetupUI:
    """Thin wrapper around the pywebview setup window."""

    def __init__(self, window):
        self.w = window

    def _js(self, code):
        try:
            if self.w:
                self.w.evaluate_js(code)
        except Exception:
            pass

    @staticmethod
    def _esc(s):
        return str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")

    def step(self, text):
        log("SETUP: " + text)
        self._js("setStep('%s')" % self._esc(text))

    def progress(self, done, total):
        if total and total > 0:
            pct = max(0, min(100, done * 100.0 / total))
            self._js("setProgress(%.1f,'%s / %s')" % (
                pct, fmt_mb(done), fmt_mb(total)))

    def indeterminate(self):
        self._js("setIndeterminate()")

    def detail(self, text):
        self._js("setDetail('%s')" % self._esc(text))

    def error(self, text):
        log("SETUP ERROR: " + text)
        self._js("setError('%s')" % self._esc(text))


# ------------------------------------------------------------- setup steps

def check_disk_space(ui):
    need = 10 * 1024 ** 3
    try:
        free = shutil.disk_usage(BASE_DIR).free
    except Exception:
        free = shutil.disk_usage(os.path.expanduser("~")).free
    if free < need:
        raise RuntimeError(
            "Not enough disk space. Need ~10 GB free, found %s." % fmt_mb(free))


def check_gpu(ui):
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            gpu = out.stdout.strip().splitlines()[0]
            log("GPU: " + gpu)
            ui.detail("GPU detected: " + gpu)
            return
    except Exception:
        pass
    log("WARNING: no NVIDIA GPU detected - processing will be very slow")
    ui.detail("No NVIDIA GPU detected - CPU mode will be very slow")


def step_python(ui):
    if os.path.exists(PYTHON_EXE):
        ui.step("Python 3.11 already downloaded")
        return
    ui.step("Downloading Python 3.11...")
    dest = os.path.join(DOWNLOAD_DIR, "python-embed.zip")
    download(PYTHON_EMBED_URL, dest, ui.progress)
    ui.step("Extracting Python 3.11...")
    ui.indeterminate()
    if os.path.isdir(PYTHON_DIR):
        shutil.rmtree(PYTHON_DIR, ignore_errors=True)
    os.makedirs(PYTHON_DIR, exist_ok=True)
    with zipfile.ZipFile(dest, "r") as z:
        z.extractall(PYTHON_DIR)
    # Enable site-packages in embeddable python (needed for pip)
    pth = os.path.join(PYTHON_DIR, "python311._pth")
    if os.path.exists(pth):
        with open(pth, "r", encoding="utf-8") as f:
            content = f.read()
        if "#import site" in content:
            content = content.replace("#import site", "import site")
            with open(pth, "w", encoding="utf-8") as f:
                f.write(content)
    # Install pip
    ui.step("Installing pip...")
    getpip = os.path.join(DOWNLOAD_DIR, "get-pip.py")
    download(GET_PIP_URL, getpip)
    subprocess.run([PYTHON_EXE, getpip, "--no-warn-script-location"],
                   check=True, creationflags=getattr(
                       subprocess, "CREATE_NO_WINDOW", 0))
    log("python + pip ready")


def step_app_zip(ui):
    dest = os.path.join(DOWNLOAD_DIR, "jpclips-pc.zip")
    ui.step("Downloading JpClips app...")
    download(APP_ZIP_URL, dest, ui.progress)
    ui.step("Extracting JpClips app...")
    ui.indeterminate()
    if os.path.isdir(APP_DIR):
        shutil.rmtree(APP_DIR, ignore_errors=True)
    os.makedirs(APP_DIR, exist_ok=True)
    with zipfile.ZipFile(dest, "r") as z:
        z.extractall(APP_DIR)
    if not os.path.exists(os.path.join(APP_DIR, "pc_server.py")):
        raise RuntimeError("App zip did not contain pc_server.py")
    log("app extracted to " + APP_DIR)


def pip_install(ui, step_text, args):
    ui.step(step_text)
    ui.indeterminate()
    ui.detail("This can take a while - see jpclips_log.txt for progress")
    log("pip install: " + " ".join(args))
    with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as lf:
        lf.write("\n--- pip install %s ---\n" % " ".join(args))
        lf.flush()
        proc = subprocess.run(
            [PYTHON_EXE, "-m", "pip", "install", "--no-warn-script-location"] + args,
            stdout=lf, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if proc.returncode != 0:
        raise RuntimeError("pip install failed: %s (see jpclips_log.txt)"
                           % " ".join(args[:3]))
    log("pip ok: " + " ".join(args[:3]))


def step_deps(ui):
    pip_install(ui, "Installing PyTorch with CUDA 12.1 (~2.5 GB)...",
                ["torch", "torchvision", "--index-url", TORCH_INDEX])
    req = os.path.join(APP_DIR, "requirements.txt")
    if not os.path.exists(req):
        raise RuntimeError("requirements.txt missing from app")
    pip_install(ui, "Installing app dependencies...",
                ["-r", req])


def run_setup(ui):
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    log("=== setup started ===")
    check_disk_space(ui)
    check_gpu(ui)
    step_python(ui)
    step_app_zip(ui)
    step_deps(ui)
    with open(VERSION_FILE, "w") as f:
        f.write(APP_VERSION)
    with open(MARKER, "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
    log("=== setup complete ===")
    ui.step("Setup complete! Starting JpClips...")


# ------------------------------------------------------- backend + webview

_backend_proc = None


def local_version():
    try:
        with open(VERSION_FILE) as f:
            return f.read().strip()
    except Exception:
        return ""


def remote_version():
    try:
        req = urllib.request.Request(
            APP_VERSION_URL, headers={"User-Agent": "JpClips-Launcher/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode().strip().split()[0]
    except Exception as e:
        log("version check failed: %r" % e)
        return None


def maybe_update_app(window):
    """Update app code only (never deps) when a new version is published."""
    if not os.path.exists(MARKER):
        return
    rv = remote_version()
    if not rv or rv == local_version():
        return
    log("app update %s -> %s" % (local_version(), rv))
    ui = SetupUI(window)
    try:
        window.evaluate_js(
            "setStep('Updating JpClips app...');setIndeterminate()")
    except Exception:
        pass
    try:
        step_app_zip(ui)
        with open(VERSION_FILE, "w") as f:
            f.write(rv)
        log("app updated to " + rv)
    except Exception as e:
        log("app update failed (keeping old version): %r" % e)


def backend_alive():
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:%d/" % PORT,
            headers={"User-Agent": "JpClips-Launcher/1.0"})
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status < 500
    except Exception:
        return False


def start_backend():
    global _backend_proc
    if backend_alive():
        log("backend already running - reusing it")
        return
    if not os.path.exists(PYTHONW_EXE):
        raise RuntimeError("pythonw.exe missing - setup did not complete")
    env = dict(os.environ)
    env["WHISPER_DEVICE"] = env.get("WHISPER_DEVICE", "cuda")
    env["WHISPER_COMPUTE"] = env.get("WHISPER_COMPUTE", "float16")
    env["MAX_CONCURRENT_JOBS"] = env.get("MAX_CONCURRENT_JOBS", "2")
    log("starting backend...")
    with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as lf:
        lf.write("\n--- backend start %s ---\n"
                 % time.strftime("%Y-%m-%d %H:%M:%S"))
        _backend_proc = subprocess.Popen(
            [PYTHONW_EXE, "-m", "uvicorn", "pc_server:app",
             "--host", "127.0.0.1", "--port", str(PORT)],
            cwd=APP_DIR, env=env,
            stdout=lf, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    log("backend pid=%s" % _backend_proc.pid)


def wait_for_backend(timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if backend_alive():
            return True
        if _backend_proc and _backend_proc.poll() is not None:
            raise RuntimeError(
                "Backend exited (code %s) - see jpclips_log.txt"
                % _backend_proc.returncode)
        time.sleep(1.5)
    raise RuntimeError("Backend did not start in %ds - see jpclips_log.txt"
                       % timeout)


def stop_backend():
    global _backend_proc
    if _backend_proc and _backend_proc.poll() is None:
        log("stopping backend pid=%s" % _backend_proc.pid)
        try:
            _backend_proc.terminate()
            _backend_proc.wait(timeout=15)
        except Exception:
            try:
                _backend_proc.kill()
            except Exception:
                pass
    _backend_proc = None


def boot(window):
    """Runs in background thread after the setup window opens."""
    ui = SetupUI(window)
    try:
        if not os.path.exists(MARKER):
            run_setup(ui)
        else:
            maybe_update_app(window)
        ui.step("Starting JpClips...")
        try:
            window.evaluate_js("setIndeterminate()")
        except Exception:
            pass
        start_backend()
        wait_for_backend()
        log("opening app window")
        window.load_url("http://127.0.0.1:%d/" % PORT)
    except Exception as e:
        tb = traceback.format_exc()
        log("BOOT FAILED: %s\n%s" % (e, tb))
        ui.error("Something went wrong:\n%s\n\nSee: %s"
                 % (e, LOG_FILE))


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    log("=== launcher started ===")
    try:
        import webview
    except ImportError:
        # Should never happen (bundled), but be graceful.
        raise RuntimeError("UI library missing - reinstall JpClipsPC.exe")

    first_run = not os.path.exists(MARKER)
    window = webview.create_window(
        APP_TITLE,
        html=SETUP_HTML if first_run else SPLASH_HTML,
        width=560 if first_run else 1280,
        height=640 if first_run else 860,
        resizable=not first_run,
    )
    window.events.closed += lambda: stop_backend()

    t = threading.Thread(target=boot, args=(window,), daemon=True)
    t.start()
    webview.start(debug=False)
    stop_backend()
    log("=== launcher exited ===")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        try:
            log("FATAL: " + tb)
        except Exception:
            pass
        # Last resort visible error (only when a console exists)
        try:
            print("JpClips failed to start. See " + LOG_FILE)
            print(tb)
        except Exception:
            pass
        sys.exit(1)
