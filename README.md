# AutoTriager — Human–AI Co-Design

**Dahe Chen · CS 5588 · Challenge 2**

An evidence-grounded incident investigation application for on-call developers and site reliability engineers.

**Status: planning.** This repository currently contains the project scope and a reviewed implementation plan. A working Streamlit application, model integration, and executed test results are not available yet.

## First essential task

Load an incident from one selected system and run an existing analysis method. Present candidate components, possible causes, supporting records, and unresolved questions so a user can inspect the evidence and record a judgment.

## Planned interaction

Select an incident → run analysis → inspect results and source records → accept, reject, or mark the result for further investigation.

The initial application will run locally with Streamlit and support English/Chinese interface switching. Calculations and record selection belong in deterministic tools; a language model may interpret the retrieved evidence. The application is read-only and does not modify production systems.

## Scope

- One system and a small set of real incident cases.
- Reuse an existing analysis method where compatible.
- Show evidence sources and missing information.
- Support basic human review in the current session.
- Test the full workflow, including failure behavior.

Multiple systems, open-ended chat, elaborate multi-agent workflows, and PR attribution are outside the initial deliverable.

## Confirmed implementation constraints

- Prefer Gemini API Free Tier; no additional paid usage is authorized. Actual model availability and project quotas still need verification. A Pro subscription is not proof that API credits have been activated.
- Local Streamlit demonstration; no public application hosting is planned.
- English/Chinese UI switching preserves the current case and feedback and does not automatically rerun analysis.
- Initially allow a few minutes per analysis; measure performance before optimizing.
- This GitHub repository is public.

## Data and method candidates

- [OpenRCA](https://github.com/microsoft/OpenRCA): proposed data and evaluation source; Bank is the first candidate to inspect.
- [EviRCA](https://github.com/yuhao541/EviRCA): candidate method to reuse, subject to license, data, environment, and API compatibility checks.

Raw-data loading and local method execution remain unverified. Evaluation answers must stay outside the application's analysis and retrieval inputs.

## Plan and review

Read the [Human–AI Co-Design plan and review (Chinese)](docs/Human_AI_CoDesign_Plan_Review_ZH.md) for the staged implementation, acceptance criteria, proposed tests, and reviewer concerns.

The [P1 specification and confirmed decisions (Chinese)](docs/P1_Specification_ZH.md) defines interface behavior, evidence contracts, failure handling, and the remaining technical checks.

## Running the application

No runnable application is included yet. Installation instructions, pinned dependencies, data setup, and execution commands will be added after the first verified implementation. Do not commit API keys or confidential data; check redistribution permissions before adding sample data.

## Planned evaluation

Approximately nine checks will cover real incident analysis, case switching, timestamp alignment, source traceability, human review, missing data, invalid references, model failures, and language switching. Controlled tests will be distinguished from independent real incidents. Diagnostic correctness and evidence support will be reported separately.

No benchmark score, performance improvement, or production reliability result is claimed.

## Course deliverables

- A working Streamlit application and reproducible GitHub repository.
- Approximately ten slides for the September 21 Human–AI Co-Design submission.
- Challenge 2 final report due September 30.

These dates are course deadlines, not claims that the deliverables have been completed.
