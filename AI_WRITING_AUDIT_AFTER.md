# AI Writing Audit (after wording-only pass)

The manuscript pass changed wording and cross-references only. No experiment,
numeric result, equation, model, or dataset was changed. The audit was rerun
after the edits.

## Before versus after

| Audit item | First pass | After pass |
|---|---:|---:|
| Extracted prose chunks | 135 | 134 |
| SAFE sentences/passages | 256 | 266 |
| REVIEW passages | 132 | 128 |
| REWRITE passages | 0 | 0 |
| GPTZero confidence | unavailable: `GPTZERO_API_KEY` absent | unavailable: `GPTZERO_API_KEY` absent |
| Claude assessment | unavailable: Anthropic key absent | unavailable: Anthropic key absent |

The local audit reports no `REWRITE` passages. The remaining `REVIEW` items are
heuristic candidates and were not mechanically rewritten. GPTZero and Claude
were not able to provide external assessments in this environment because the
required credentials were not configured.

Full post-pass details are in [AI_WRITING_AUDIT.md](AI_WRITING_AUDIT.md). Raw
GPTZero output is stored at `.ai-audit/gptzero_raw.json`.
