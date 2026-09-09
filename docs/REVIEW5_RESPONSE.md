# Response to external review #5 (2026-09-07)

Verdict: **Borderline**, lower edge of the accepted band. **Critical 0, Major 3, Must-Fix 3,
and "Acceptance-critical experiment: None."** All three Majors are framing, and the review
says so directly: *"현재 문제는 실험 수 부족보다는 논문의 conceptual thesis가 얼마나 명확히
기억되느냐입니다."*

## Must-fix 1 — singularize the contribution as a timestamp-semantics mismatch

The contribution list read as a set of measurements ("three measurements and one bound"),
which invites the reading that the paper carefully quantifies expected behaviour. **Applied**
in the abstract and the introduction, in the review's own terms:

> That timestamp does not uniquely specify the temporal support of either side of the
> comparison. Event-detection benchmarks collapse three quantities into it: a predictor's
> evidence support, its effective output time, and the exposure-conditioned support of the
> labels. This paper separates and measures each from released artifacts.

The introduction's bridge sentence now names the same three quantities instead of counting
measurements.

## Must-fix 2 — subordinate `output ≈ label`, foreground the separation

`tau ≈ 0` is what the training objective encourages, and presenting it as a headline invites
"of course it predicts the supervision timestamp". **Applied** in the abstract and
Sec. 3.6:

> ... place the output time at the label instant, which its training objective encourages;
> what the measurement adds is that this output time stands 3.81 standard errors from the
> window's own centroid.

The review's suggested wording used a "not X but Y" construction, which item 188 of the
project checklist forbids; the substance is kept and the construction is not.

## Must-fix 3 — the DSEC result is an identifiability bound, not an error magnitude

**Applied** in the abstract, Sec. 4.4 and the conclusion:

> That is an identifiability bound and not a timing error: a per-object temporal statistic
> measured inside one of these exposures cannot be attributed to object timing until the
> illumination-driven structure is separated from it.

Framed this way the small spatial magnitude stops reading as a weakness. It is what a
bounded negative result looks like.

## What was not done

The review's three candidate experiments are each marked as not grounds for a Weak Reject.
The most valuable, a second released detector, would reduce the generality objection; it is
recorded here as the next step rather than a submission blocker, consistent with the
review's own answer of "Borderline" to whether its absence justifies a Weak Reject.

## Cumulative record of the five external reviews

| # | verdict | Critical | what it changed |
|---|---|---|---|
| 1 | Reject | all core results unmeasured | the measurements were run |
| 2 | Reject | integer-period cancellation false | E12 and E18 withdrawn |
| 3 | Reject | magnitude regression does not identify a lag | the estimator was rebuilt (E27–E33) |
| 4 | Borderline | 0 | four framing fixes; the title |
| 5 | Borderline | 0 | three framing fixes; the thesis sentence |

Reviews 4 and 5 both report **zero Critical findings** and **no acceptance-critical
experiment**. What each asked for, and what was delivered, was a sharper statement of what
the measurements mean.
