# Week 1

- **Zoom:** [lesson notebook](HMSTI_509_M1_Lesson.ipynb).
- **In person:** [studio instructions](studio/README.md).

## Setup

Clone the complete repository and open it in VS Code. From the repository root:

```text
cd rag-starter
python -m venv .venv
```

Use `python3` or `py` if that is your Python command. Activate the environment:

**macOS / Linux:**

```sh
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

Install the notebook kernel and check the starter:

```text
python -m pip install ipykernel
python scripts/check_env.py
```

In VS Code, open the lesson notebook and select `rag-starter/.venv/bin/python`
(Windows: `rag-starter/.venv/Scripts/python.exe`) as the kernel. Run cells from the top.
The notebook locates `rag-starter` in this checkout. Week 1 needs no model API key.

The health check and studio Arena need only Python 3.10+, so you can use them even
if notebook installation is blocked. See [setup troubleshooting](../rag-starter/SETUP_TROUBLESHOOTING.md).
Later dependencies are listed in `rag-starter/requirements.txt`.

Save your project scope and evidence in your own project repository. Follow the
[Git checklist](studio/GIT_CHECKLIST.md) to copy the starter and push your own work.
