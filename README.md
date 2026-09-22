# AutoTriager

**A local incident investigation application for CS 5588 Human–AI Co-Design.**

Select a recorded Bank incident, run an existing evidence-extraction method with Gemini reasoning, inspect original records, and record a human judgment. The application supports English and Chinese. It is read-only and operates on offline telemetry.

## Implemented scope

- Two real OpenRCA Bank development cases, preserving full-day baselines and corresponding logs/traces.
- Pinned EviRCA data adapters, anomaly extraction and investigation tools.
- A bounded Gemini tool loop with explicit failure and unresolved states.
- Evidence IDs linked to source files, CSV record numbers, components and timestamps.
- Accept/reject/unresolved feedback, associated with the current run and exportable as JSON.
- English/Chinese UI switching that preserves results without calling the model.

This is an **engineering adaptation**, not a complete reproduction of the EviRCA paper. Diagnostic correctness and successful execution are evaluated separately. See [implementation decisions](docs/Implementation_Decisions.md) and [validation results](docs/Validation_Report.md).

## Local setup (Windows Command Prompt)

Requirements: Python 3.12, Git, internet access, approximately 6 GB of free disk space, and a Gemini API project that you have confirmed is on Free Tier. A Google AI Pro subscription alone is not an API billing configuration.

```bat
git clone https://github.com/chendahe666/AutoTriager-CoDesign.git
cd AutoTriager-CoDesign
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\bootstrap.py
.venv\Scripts\python.exe scripts\fetch_bank.py
.venv\Scripts\python.exe scripts\prepare_cases.py
```

The data script extracts March 4 and March 6, 2021 from the official Bank archive using byte ranges. It preserves full days, verifies ZIP CRCs, and records SHA-256 hashes in `data/download_manifest.json`. The first download transferred approximately 537 MB and extracted approximately 4.6 GB. Downloads depend on the upstream host.

Set `GEMINI_API_KEY` through Windows **Edit environment variables for your account → User variables → New**. Never paste a key into the repository, a screenshot or a chat. The application reads the process environment and, on Windows, the current user's environment settings. It does not display or save the key.

```bat
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the URL printed by Streamlit. The server binds to `127.0.0.1`. The app fixes the model to `gemini-3.1-flash-lite`, allows at most six requests per run and sets a 60-second per-request timeout. One temporary HTTP 5xx error may be retried **within** that six-request budget. No paid or alternate model fallback is implemented. Clicking **Run analysis** explicitly starts a new run. UI language and evidence selection do not start analysis.

Google can change availability, free quotas and pricing. Confirm your project's tier before using a key. This app does not enable billing or infer billing status from a key. [Official pricing](https://ai.google.dev/gemini-api/docs/pricing).

## Data and evaluation separation

- Runtime instructions: `data/cases.json`.
- Runtime observations: `data/Bank/telemetry/`.
- Scoring labels: `data/evaluation_only/labels.json`, used only by evaluation scripts.
- The original `query.csv` contains labels. Only preparation reads it; the application never opens it.
- Local runs: `runs/`, containing evidence and model output, not credentials.
- Human feedback stays in the session unless the user exports it.

Both cases were discussed during design and are development cases, not a held-out benchmark. Nine checks are not nine independent incidents. Source linkage does not prove causality. A full-day baseline includes observations after the incident, making this a retrospective investigator rather than an online detector.

## Tests

```bat
.venv\Scripts\python.exe scripts\run_cases.py
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\evaluate_runs.py
```

The first command makes real Gemini requests. Checks requiring real outputs skip if none exist. They do not manufacture successful results. For the browser test, start the app on port 8502 and use a second terminal:

```bat
.venv\Scripts\python.exe -m playwright install chromium
.venv\Scripts\python.exe scripts\browser_check.py
```

The browser test makes a real request and records explicitly labeled test feedback. See [validation results](docs/Validation_Report.md) for successes, failures and limitations.

## Sources and reuse

| Resource | Role | Reference |
|---|---|---|
| OpenRCA | Bank data, questions, official scorer | https://github.com/microsoft/OpenRCA |
| EviRCA | Adapter, evidence extraction, investigation tools | https://github.com/yuhao541/EviRCA |
| Gemini | Interpretation with constrained tool calls | https://ai.google.dev/gemini-api/docs/openai |
| Streamlit | Local interface and human review | https://docs.streamlit.io/ |

`bootstrap.py` retrieves reviewed commits into ignored `vendor/`. EviRCA's inspected revision had no license file; this repository does not redistribute it or claim rights to it. Public access is not a blanket reuse license. Respect upstream terms; redistribution or commercial use would require clarification from its authors. OpenRCA code is MIT licensed. Raw telemetry is downloaded from the official source and not republished here.

Dahe Chen defined the scope, priorities, budget, language and review interaction. Codex implemented the application and ran automated checks. Automated test feedback is not Dahe Chen's acceptance.
