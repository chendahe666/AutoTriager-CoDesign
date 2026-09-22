# Validation report

**Date:** September 21, 2026. **Scope:** a local Windows development demonstration, not a production study. **Human acceptance:** pending; Dahe Chen chose to review later while implementation delivery continues.

## Data and method

Two real OpenRCA Bank instructions were selected before implementation: query row indices 1 and 4 (zero-based), both `task_6`, requiring component and reason. The complete relevant days of metrics, logs and traces were downloaded from the official Bank archive. The downloaded archive members have CRC and SHA-256 records locally. No incident was fabricated.

Runtime inputs exclude scoring labels and previous baseline predictions. The two incidents were already discussed during design, so they are development cases. Full-day baselines make the task retrospective. Method: pinned EviRCA evidence and read-only tools, with an application-owned bounded Gemini 3.1 Flash-Lite loop and output validation.

## Selected real runs

| Case / run | Observed output | Requested-field score | Total time |
|---|---|---|---|
| bank-001 / 319be82eec24 | Redis02; high memory usage | 1.0 | 84.75 s |
| bank-004 / 61d22bf8c6fa | Tomcat04; specific network reason unresolved | 0.5 | 155.72 s |
| Browser / d6c075bd0a6d | Redis02; high memory usage | 1.0 | 130.08 s |

These are individual results, not an aggregate accuracy estimate. The official OpenRCA scorer checks the requested fields. An unresolved requested reason remains incorrect; abstention is not counted as a correct diagnosis. Different cold preparation and cache conditions explain part of the timing variation. Remote service delays also vary.

## Full attempt audit

The following development attempts are retained, including failed ones. The code changed between attempts; this is a debugging audit, not a controlled model comparison.

| Run ID | Case | Outcome | Official partial score |
|---|---|---|---|
| 319be82eec24 | bank-001 | Complete | 1.0 |
| 714bf4d89a85 | bank-004 | HTTP 503, no diagnosis | 0.0 |
| 03a6c514c08c | bank-001 | HTTP 503 after tool calls | 0.0 |
| 980cfeb39ef8 | bank-004 | Citation validator rejected system-level evidence; budget exhausted | 0.0 |
| e55946bb2a89 | bank-001 | Complete; UI feedback restoration check failed | 1.0 |
| 2ab481cbc0d5 | bank-001 | Complete; UI form restoration still failed | 1.0 |
| 61d22bf8c6fa | bank-004 | Component identified; reason unresolved | 0.5 |
| d6c075bd0a6d | bank-001 | Complete; final real browser checks passed | 1.0 |

An earlier preparation failed on the real business metric table because its transaction identifier is `tc`, not `cmdb_id`; the data adapter was corrected before any model call. An initial pytest attempt had an environment permission error for its temporary directory; it was rerun in an authorized project directory.

Fixes prompted by the audit:

- Permit system-level golden signals as supporting evidence, while requiring at least one component-specific source.
- Keep specific network latency/loss causes unresolved in this MVP.
- Allow one transient HTTP 5xx retry within the existing six-request limit, and keep explicit failure behavior.
- Restore saved review values when returning to a case; language changes and case changes no longer erase the saved judgment.
- Preserve prepared raw records even when the first API request fails.

## Nine engineering checks

Final command: `python -m pytest tests -q`. Result: **9 passed**. The suite uses completed real output where needed, with explicit synthetic inputs for failure and state tests. It skips real-output checks if no completed run exists. The all-attempt table above separately records API failures.

| Check | What was checked | Kind |
|---|---|---|
| T1 | Real completed case includes model calls, candidates and existing evidence IDs | Recorded integration output |
| T2 | Different case cannot display another case's result | State contract |
| T3 | UTC+8 question window and seconds/milliseconds conversion | Actual inputs |
| T4 | Sampled cited original CSV records resolve and match stored values | Actual file audit |
| T5 | Feedback requires a reason and retains case/run identity | State contract |
| T6 | Removing required metrics changes the cache key and stops before analysis | Controlled missing-file fixture |
| T7 | Nonexistent evidence ID is rejected | Injected invalid citation |
| T8 | Simulated timeout makes no diagnosis and retains prepared observations | Injected API failure |
| T9 | Both interface languages have all defined static labels | Translation contract |

Additional actual browser interaction checks passed on run `d6c075bd0a6d`: real analysis, evidence rendering, feedback, JSON export, language switching with the same run/request count, case isolation, and restoration of saved feedback. Browser feedback states explicitly that it is an automated test, not Dahe Chen's acceptance. Screenshots in this repository come from those actual interactions.

## Source and claim audit

- In the March 4 metrics, CSV data record **956231** contains Redis02's `OSLinux-OSLinux_MEMORY_MEMORY_NoCacheMemPerc` at timestamp `1614852840`, value **92.6839**. EviRCA displays the rounded peak 92.684.
- The component/memory answer matches the benchmark, and the raw metric supports a substantial excursion. It does not independently prove the entire explanation of application impact.
- The March 6 component matches the label. The tool supplies simultaneous business `rr` and `mrt` changes. Exact interpretation of all abbreviated business KPIs needs source documentation; generated prose should not substitute for that documentation.
- Citation checks prove existence and component/scope linkage, not sentence-level entailment. Raw-record tests sample cited records; they do not establish that every narrative claim is supported.
- Observed onset can differ from the hidden time label and between model outputs. These two questions do not request onset, so their scores cannot validate time localization.

## Limitations and next validation

Two development cases do not establish reliability on unseen incidents, causal recovery accuracy, engineer time savings, or superiority to EviRCA. Free API service errors occurred. The current method can leave required fields unresolved. Upstream Bank traces cover a subset of components. The app's local source references depend on downloaded files remaining available.

The next human step is to inspect the interface and decide whether the explanation and evidence are useful. Additional unseen cases should precede any broad accuracy claim. Rich component comparison and bounded follow-up are planned for Challenge 3; systematic missing-data variants are planned for Challenge 4.

Sources: [OpenRCA and scorer](https://github.com/microsoft/OpenRCA), [EviRCA](https://github.com/yuhao541/EviRCA), [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing).
