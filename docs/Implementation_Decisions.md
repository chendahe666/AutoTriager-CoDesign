# Implementation decisions

## Human decisions retained

Dahe Chen chose an engineering implementation, one system, reuse of existing work, a first P1 combining data loading and algorithm execution, inspectable evidence and human accept/reject/unresolved feedback. He selected Gemini Free Tier, local Streamlit, Chinese/English switching, a few-minute initial wait and a public code repository. Multi-system support remains optional. The application does not modify production or review PRs.

## AI implementation work

Codex inspected pinned upstream code, downloaded two full days of real Bank telemetry, and implemented input checks, source indexing, model calls, state handling, localization, feedback export and validation. Automated test feedback does not imply human approval.

EviRCA is loaded unchanged from commit `bc11c06932717751f68b8ed7da6d31f5c23c952c`. The app calls its Bank adapter, query parser, series baselines, log/trace builders, anomaly entries and investigation tools. It adds its own orchestration around those functions.

## Adaptations

1. Gemini 3.1 Flash-Lite uses Google's OpenAI-compatible endpoint. The older 2.5 Flash-Lite returned HTTP 404 for this account; 3.1 returned a real response and has a published free tier.
2. The reasoning loop allows six requests at most, one HTTP 5xx retry within that budget, a 60-second timeout, and bounded output. The model has no shell or open web tool.
3. Output includes nullable reasons, evidence IDs and limitations. The original runner/formatter can force an answer count or create fallback guesses. Those paths are not used.
4. A deterministic index links tool observations to original files and CSV record ordinals. Samples are bounded; computation scope is separate. Record numbers exclude the header and may differ from physical text lines.
5. Input file sizes, modification times and missing-file markers form the preparation cache key. Upstream caches are cleared before fresh preparation because their original keys omit file versions.
6. Only public telemetry observations go to Gemini. Keys remain local. Raw data and upstream checkouts are ignored by Git.
7. Interface translations are local. Switching language preserves source identifiers, results and feedback without API calls. Existing generated explanations retain their original language.
8. The Bank MVP withholds a specific network latency/loss reason because its observations do not reliably discriminate them. If the model nevertheless proposes one, the application preserves that proposal in metadata and displays an unresolved reason. A requested unresolved reason is scored as incorrect.

These are engineering changes, so results are not an exact reproduction or a fair direct comparison with published paper accuracy.

## Review contract

- New analysis clears the previous visible result for that case before preparation begins.
- Each output includes case/run IDs, data fingerprint, upstream revision, model, usage and elapsed time.
- Human judgment requires a reason and belongs to a particular run. It is not an evaluation label or training example.
- Citation validation checks existence and component linkage. It does not establish causal correctness or sentence-level entailment.
- Missing mandatory metrics stop before model calls. Optional missing records are listed. API failure returns an incomplete state without a manufactured diagnosis.
- The whole-day baseline is retrospective. Bank traces cover some components and cannot resolve every network cause.

## Remaining human decisions

Final course submission, personal acceptance of a diagnosis, future paid use, replacement of the main method/data and public hosting remain with the user. Routine fixes, testing and documentation are delegated to Codex. No new product decision was needed to implement this scope.
