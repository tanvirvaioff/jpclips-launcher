# JpClipsPC.exe — desktop launcher for JpClips PC

Small Windows exe (~50–60 MB). Double-click it:

1. **First run** — opens a setup window, downloads everything into
   `%LOCALAPPDATA%\JpClips` (portable Python 3.11, PyTorch CUDA 12.1,
   all app deps, the JpClips app itself). Downloads resume if interrupted.
2. **After setup** — starts the backend silently and opens JpClips in a
   desktop window (WebView2). No browser, no console window.
3. **Closing the window** stops the backend.
4. **Later runs** — checks for app updates (code only, deps untouched) and
   opens straight away.
5. Errors go to `%LOCALAPPDATA%\JpClips\jpclips_log.txt`.

## Files

- `launcher.py` — the whole launcher (pywebview UI + setup + backend mgmt)
- `app_version.txt` — bump when the app zip changes → launcher auto-updates
- `.github/workflows/build.yml` — builds `JpClipsPC.exe` on windows-latest

## App zip

`app/jpclips-pc.zip` is committed to this repo — the launcher downloads it
from the permanent raw URL (no expiry). Bump `app_version.txt` when the
zip changes and the launcher auto-updates the app code (deps untouched).
