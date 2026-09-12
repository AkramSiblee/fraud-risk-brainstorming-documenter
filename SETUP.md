# Setup Guide — First-Time Install

This guide is for someone opening this folder for the first time on a
computer that has **none** of the required tools installed yet (e.g. a
new laptop, or a client machine). Written for Windows; macOS/Linux notes
are called out where they differ.

## What you need, in order

| # | Tool | Why it's needed | Where to get it |
|---|------|------------------|------------------|
| 1 | **VS Code** | The editor you'll open this folder in | https://code.visualstudio.com |
| 2 | **Node.js (LTS)** | Installs the Claude Code CLI | https://nodejs.org |
| 3 | **Claude Code** | The agent that reads `CLAUDE.md` and runs the pipeline | `npm install -g @anthropic-ai/claude-code`, or the "Claude Code" extension from the VS Code marketplace |
| 4 | **A Claude account** | Claude Code needs to sign in — a Claude Pro/Max login or an Anthropic API key both work | Sign in the first time you launch `claude` |
| 5 | **Python 3.9+** | Runs the deterministic parts of the pipeline (ingest/boilerplate/flag/export) | https://python.org — **check "Add python.exe to PATH"** during install |
| 6 | **Python packages** | `openpyxl` (Excel output) and `python-docx` (Word output) | `pip install -r requirements.txt` (step 3 below) |

No Anthropic API key is required for the pipeline's judgment logic itself —
that step runs inside Claude Code directly, not as a separate API call
(see `CLAUDE.md`). You only need *some* way to sign Claude Code in.

## First-run steps

1. **Get the folder.** Either unzip a copy someone sent you, or clone it:
   ```
   git clone https://github.com/AkramSiblee/fraud-risk-brainstorming-documenter.git
   ```
   (Cloning needs **Git for Windows**: https://git-scm.com — skip this if
   you were handed a zip instead.)

2. **Open it in VS Code.** File → Open Folder... → select this folder.

3. **Open a terminal in VS Code** (Terminal → New Terminal) and run:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   macOS/Linux: `source .venv/bin/activate` instead of `.venv\Scripts\activate`.

4. **Launch Claude Code** in that same terminal:
   ```
   claude
   ```
   The first launch prompts you to sign in — follow the browser prompt.

5. **Start the pipeline.** Once signed in, just ask Claude Code to run the
   pipeline against an input package (or point it at your own). Claude Code
   reads `CLAUDE.md` automatically and follows the operating sequence there.
   To sanity-check the install works, try:
   ```
   python src/cli.py ingest sample_input/thornbury -o working/ingested.json
   ```
   If that produces `working/ingested.json` without errors, everything above
   is installed correctly.

## Troubleshooting

- **`python` / `pip` not recognized** — Python wasn't added to PATH during
  install. Re-run the Python installer and check "Add python.exe to PATH",
  or search "Environment Variables" in Windows and add the Python install
  folder manually.
- **`claude` not recognized** — Node.js/npm didn't finish installing, or a
  new terminal wasn't opened after installing. Close and reopen the VS Code
  terminal after installing Node.js.
- **`pip install` fails** — make sure the virtual environment is activated
  first (you should see `(.venv)` at the start of the terminal prompt).
