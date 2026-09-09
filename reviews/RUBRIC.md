# CVPR20 reviewer protocol

Ten reviewers judge every round. A round passes only when **all ten** return ACCEPT or
STRONG ACCEPT. One REJECT sends the work back to idea generation; one BORDERLINE sends it
back for revision.

## Grounding requirement

A reviewer's authority comes from real papers, not from taste. Before scoring, each
reviewer fetches and names at least five **actually accepted** CVPR/ICCV/ECCV papers from
2024-2026 in or adjacent to the topic, and scores the submission against what those papers
actually did. Cite title, venue, year. A reviewer who cannot name its comparison set is
disqualified for that round.

## Verdict scale

- **STRONG ACCEPT** — would fight for it in the AC discussion.
- **ACCEPT** — above the bar; remaining issues are fixable in the rebuttal.
- **BORDERLINE** — one unfixed structural problem; name it in a single sentence.
- **REJECT** — a fatal flaw. Name it, and say whether it is fatal to the idea or only to
  this execution of it.

## What each reviewer must return

1. Verdict, one of the four above.
2. Summary of the submission in three sentences, written as a reviewer who is proving they
   read it, not as a summary of the abstract.
3. The single strongest reason to accept.
4. The single strongest reason to reject.
5. Every factual error found, with the location and the correction.
6. Every claim whose strength exceeds its evidence, quoted.
7. The experiment a hostile reviewer would demand, and whether its absence is fatal.
8. A ranked list of required fixes, most important first.

## Standing failure modes to check

- A result that only exists in simulation, with no real-data confirmation.
- A metric invented by the authors on which, unsurprisingly, the authors win.
- A "first to" claim that a fifteen-minute search defeats.
- A contribution that reduces to a new fusion module or a new loss term.
- Numbers in the text that do not match the numbers in the tables.
- Baselines that are weaker than the published state of the art, or run with defaults the
  original authors would not recognise.
- Compute claims incompatible with the hardware the work actually ran on.
- An ablation set that never removes the component the whole paper rests on.
