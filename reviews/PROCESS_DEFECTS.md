# Process defects in the idea round — recorded 2026-09-01

Written so that a later reader knows which conclusions rest on clean process and which do not.

## 1. The shared web-search budget was exhausted

The ten idea teams drew on one 200-call search budget and used it up. Teams 2, 3, 5, 7 and 8
each reported an unfinished prior-art sweep, and named the specific checks they could not run.
**Consequence:** every novelty claim from the idea round is provisional. Reviewer 5 was
tasked with an independent collision hunt, and no idea should be committed to before that
review lands.

## 2. Reviewers may have read a stale copy of team06

The reviewers were launched at about 15:22. `team06.md` was still being written and its last
write landed at **15:24:05**, growing from 495 to 578 lines. The reviewers therefore read a
version missing up to 83 lines.

This matters more than the line count suggests, because the material added at the end was
**three retractions**, all of which weaken the idea:

- "EDI is wrong" — **false**; mEDI Eq. (5) already carries the term. Retracted.
- "Every event-frame method assumes the point-sample identity" — **false**; EVDI Eq. (19)-(20)
  already implements the exposure-correct two-frame loss. EVDI was promoted to a positive
  control.
- "The contrast threshold's motion dependence is unreported" — **false**; Delbruck CVPRW 2021
  gives the rate law. Cited rather than claimed.

Team 6 also lowered its own novelty score from 7 to 6.5 on the strength of these.

**Consequence:** any reviewer verdict on team06 that reads more favourably than the team's own
final self-assessment should be treated as uncalibrated. If team06 reaches the shortlist, it
must be re-reviewed against the final file before anything is decided. If it does not reach
the shortlist, this defect changes nothing.

## 3. What was verified independently of the agents

The measurements in `../experiments/` were made in the main session, not by any idea team:
the DSEC exposure survey (E00), the intra-exposure event count (E01), and the RVT window
alignment check (E02). These stand regardless of the two defects above.
