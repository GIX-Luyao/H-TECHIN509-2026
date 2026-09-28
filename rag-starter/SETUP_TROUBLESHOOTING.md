# Setup Troubleshooting — the known failures (Windows first)

Most of this cohort works on corporate Windows machines, and every failure below has
happened to a real student. Find your symptom, apply the fix, move on. **Setup problems are
never graded** — see the last section.

---

## 1. `uv` install is blocked (corporate proxy / cert errors)

**Symptom:** the `uv` installer script hangs, errors with `SSL`/`proxy`/`403`, or IT policy
blocks the download entirely.
**Cause (one line):** corporate proxies intercept HTTPS downloads and block unknown installers.

**Fix A — install uv through pip** (pip is usually already sanctioned):

```powershell
# Windows (PowerShell)
py -m pip install uv
```

```bash
# macOS / Linux
python3 -m pip install uv
```

**Fix B — skip uv entirely** (fully supported all term — plain venv + pip):

```powershell
# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Everywhere the course says `uv pip install ...`, plain `pip install ...` works the same.

---

## 2. PowerShell won't activate the venv

**Symptom:** `.venv\Scripts\Activate.ps1` fails with *"running scripts is disabled on this
system"*.
**Cause (one line):** PowerShell's execution policy blocks all scripts by default.

```powershell
# Windows (PowerShell) — allow local scripts for YOUR user only (no admin needed):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1

# If policy is locked by IT, use cmd.exe instead — no policy involved:
.venv\Scripts\activate.bat
```

```bash
# macOS / Linux — no execution policy; just:
source .venv/bin/activate
```

You know it worked when `(.venv)` appears at the start of your prompt.

---

## 3. "python is not recognized" / the wrong Python runs

**Symptom:** `python` is not found, opens the Microsoft Store, or runs an old version.
**Cause (one line):** Python isn't on your PATH — or a different Python is found first.

```powershell
# Windows (PowerShell) — use the py launcher; it finds Python regardless of PATH:
py --version
py -m venv .venv

# See which pythons exist and which one is first on PATH:
py -0
where.exe python
```

```bash
# macOS / Linux — use python3 explicitly and check what it points at:
python3 --version
which python3
```

**The rule that ends most PATH pain:** once your venv is **activated**, plain `python`
always means the venv's Python — on every OS. Activate first, then stop thinking about PATH.
(If the Store keeps opening on Windows: Settings → Apps → Advanced app settings → App
execution aliases → turn off the two `python` aliases.)

---

## 4. `SSL: CERTIFICATE_VERIFY_FAILED` on a corporate machine

**Symptom:** `pip`/`uv` installs fail with `CERTIFICATE_VERIFY_FAILED`.
**Cause (one line):** your company's proxy re-signs HTTPS traffic with its own certificate,
which Python doesn't trust yet.

**Sanctioned fixes, in order:**

1. **Ask IT for the corporate root certificate** (they have a standard answer for this),
   then point pip at it:

   ```powershell
   # Windows (PowerShell)
   pip config set global.cert C:\path\to\corporate-root.pem
   ```

   ```bash
   # macOS / Linux
   pip config set global.cert /path/to/corporate-root.pem
   ```

2. **Try your phone hotspot or home network** — if installs succeed there, it is
   definitively the proxy, which strengthens your ask to IT.
3. **When to just use a personal machine:** if IT can't help within a day, do the course on
   a personal laptop and keep the work machine for reading. Do NOT paste
   `--trusted-host`-style bypasses from random forums onto a corporate machine — that
   disables certificate checking and can violate your IT policy.

---

## 5. `chromadb` won't install

**Symptom:** `pip install chromadb` fails with compiler errors ("Microsoft Visual C++ 14.0
required"), long-path errors, or proxy timeouts.
**Cause (one line):** chromadb pulls in native dependencies that need build tools, long
paths, and a clean network — three things corporate Windows often lacks.

**The tested workaround (fully supported all term):** skip Chroma and use the in-memory
store — same interface, pure Python, zero installs:

```python
from ribot.vectorstore import get_store
store = get_store(persist=False)   # InMemoryStore — this is the default
```

Every notebook, exercise, and test in the course works on this path. Chroma only adds
persistence between runs. If you still want it:

```powershell
# Windows (PowerShell) — enable long paths (admin), then retry:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
pip install chromadb
# Compiler error? Install "Microsoft C++ Build Tools" from visualstudio.microsoft.com, or stay in-memory.
```

```bash
# macOS — usually just works; if not:
xcode-select --install
pip install chromadb
```

---

## 6. When to stop debugging

**The rule: 30 minutes, then post and move on.** Copy the *exact* error (text, not a
screenshot) into the cohort channel, note what you already tried, and continue with the
offline / in-memory path — the whole course is designed to keep working. A classmate lost a
Saturday to a PATH problem that took ten minutes to fix in class. Don't donate your weekend:
**setup problems are never graded**, and neither is asking for help.
