# E03 — Availability of the two blocking datasets (measured 2026-09-01, main session)

The area-chair review flagged two datasets as blocking, each on the critical path of
several ideas. Both claims were checked directly rather than accepted.

## FE108 / FE240hz — NOT gated. The claim that it is, is wrong.

Reported by an idea team as "application-gated", and by the area-chair review as
"the host refuses connections". Neither is true today.

| probe | result |
|---|---|
| `https://zhangjiqing.com/dataset/` | HTTP 200 |
| `https://zhangjiqing.com/publication/iccv21_fe108_tracking/` | HTTP 200 |
| `github.com/Jee-King/CVPR2022_STNet` README | HTTP 200, contains the download links |
| Google Drive folder `1pNY8kahrof9l9zCw7TtXY4RhvJ4GGx37` | HTTP 200, 308 KB of listing |
| `gdown.download_folder(..., skip_download=True)` | **listed 2 files, no auth** |

Files enumerated:

    img_120_5_split/val.zip
    img_120_split/val.zip

`gdown` 6.1.0 is on pypi and installs inside the container. The STNet README describes
these as the *preprocessed test set* of FE240hz and points to the author's publication page
for the whole dataset. VisEvent's preprocessed test set is shared the same way
(`1nrHaJysllPOq0VxA1p-Q-4WOr6IVrqO-`).

**Correction to the paragraph above — the full dataset IS gated.** Re-reading the dataset
page's own text settles it. `zhangjiqing.com/dataset/` carries the line:

> Download Application for Access for Non-Commercial Use

with a single OneDrive link, which is the application form, not the data. So the accurate
statement is a split one:

| what | status |
|---|---|
| **Full FE108 / FE240hz, with the 240 Hz Vicon ground truth** | **application-gated.** A form must be filled and sent; turnaround unknown. |
| **Preprocessed FE240hz val/test split** (STNet's Google Drive) | **open.** Enumerated above with `gdown`, no auth. |
| VisEvent preprocessed test split | open, same mechanism |

**Consequence.** Ideas 1, 2, 4 and 7 stake their primary real-data figure on the 240 Hz
ground truth, and that part is genuinely gated — their risk assessment was right and my
first reading of it was wrong. What changes is the *shape* of the risk: an open val/test
split exists, so a smaller version of the real-data figure can be produced on day one
without waiting for an application, and the application only gates the full-scale version.
Any plan that depends on FE240hz should send the application immediately and design its
week-1 figure against the open split.

## BS-ERGB — effectively dark. The claim that it is, holds.

| probe | result |
|---|---|
| `https://rpg.ifi.uzh.ch/timelens/` | HTTP 200, but the body is a 126-byte stub |
| `https://rpg.ifi.uzh.ch/TimeLens.html` | HTTP 200, links to `timelens++download.html` |
| `https://rpg.ifi.uzh.ch/timelens++download.html` | **HTTP 200, and contains no download link at all** — 5062 bytes of site navigation, no form, no email gate, nothing to request |
| `https://uzh-rpg.github.io/timelens-pp/` | HTTP 200 |
| guessed archive paths under `download.ifi.uzh.ch/rpg/` | 404 |

The download page exists and is empty of downloads. That is worse than a gate, because
there is no one to ask. **No idea may keep BS-ERGB on its critical path.** Several used it
specifically to rebut "your effect is a simulator artefact"; that rebuttal now needs a
different dataset, and picking it is a required revision, not an optional one.

## Standing correction to the review record

Reviewer 9 reported FE108's host as refusing connections. It does not. Reviewer 9's
downstream reasoning about ideas 1, 2, 4 and 7 was therefore built on a false premise and
those parts of that review should be discounted.
