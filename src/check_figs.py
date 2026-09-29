#!/usr/bin/env python3
"""Check that every figure the submitted manuscript includes is present and is the
byte-identical output of the script that renders it.

main.tex draws figures through \\figasset, which falls back to a framed box reading
"asset not yet rendered" when the file is missing.  That fallback is deliberate -- the
source compiles before the assets exist -- but it also means a missing figure produces a
PDF that looks finished, at the right page count, with a box where a measurement should
be.  Nothing else in the repository fails in that case.

The second thing checked here is where the renderers write.  Every one of them writes to
paper/figs/, which is *not* the directory the submitted manuscript reads: that is
submission_2027/paper/latex/figs/.  Re-running a renderer therefore updates a copy the
compiled PDF ignores, and the figure in the submission stays as it was until someone
copies it across by hand.  This script makes that copy step verifiable instead of
remembered, by requiring the two files to be equal byte for byte.

Run:        python3 src/check_figs.py
Elsewhere:  PAPER_DIR=/tmp/somewhere python3 src/check_figs.py
Self-test:  bash src/check_figs_selftest.sh
Exit status is the number of problems, so 0 means all clear.  This script writes nothing.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.environ.get("PAPER_DIR") or os.path.join(ROOT, "submission_2027/paper/latex")
EMITTER_DIR = os.path.join(ROOT, "paper", "figs")

# The script that renders each asset, read off its own savefig call.  A figure whose
# renderer is unknown is reported rather than skipped: an asset nobody can regenerate is
# the same problem as one that has drifted.
EMITTER = {
    "fig1_dsec_exposure.pdf": "src/make_figs.py",
    "fig3_day_night.pdf": "src/make_figs.py",
    "fig_predictor.pdf": "src/make_figs.py",
    "chunkpos.pdf": "src/e58f_fig.py",
    "chunkpos_full.pdf": "src/e58f_fig.py",
    "paired_frame.pdf": "src/e60_fig.py",
    "fig5_qualitative.pdf": "src/make_fig_qualitative.py",
    "fig6_sweep_real.pdf": "src/make_fig_real.py",
    "fig7_ceiling_vs_day.pdf": "src/make_fig_real.py",
}


def rel(p):
    return os.path.relpath(p, ROOT)


def asset_paths():
    """The \\figasset arguments of every .tex in the paper directory, in file order."""
    out = []
    for name in sorted(os.listdir(PAPER)):
        if not name.endswith(".tex"):
            continue
        txt = open(os.path.join(PAPER, name), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"\\figasset\{([^}]*)\}", txt):
            out.append((name, m.group(1)))
    return out


def main():
    problems = 0
    if not os.path.isdir(PAPER):
        print(f"FAIL: {PAPER} is not a directory; nothing was checked")
        return 1
    found = asset_paths()
    if not found:
        print(f"FAIL: no \\figasset call in any .tex under {rel(PAPER)}; either the "
              "manuscript stopped using the macro or this script is pointed at the "
              "wrong directory, and in both cases nothing was verified")
        return 1
    for tex, ref in found:
        target = os.path.join(PAPER, ref)
        base = os.path.basename(ref)
        if not os.path.exists(target):
            print(f"FAIL: {tex} includes {ref}, which does not exist, so the PDF carries "
                  f"an 'asset not yet rendered' box there; run {EMITTER.get(base, '?')} "
                  f"and copy its output into {rel(os.path.dirname(target))}")
            problems += 1
            continue
        src = EMITTER.get(base)
        if src is None:
            print(f"FAIL: {tex} includes {ref}, which no known script renders; add its "
                  "renderer to EMITTER in this file or the asset cannot be regenerated")
            problems += 1
            continue
        if not os.path.exists(os.path.join(ROOT, src)):
            print(f"FAIL: {ref} is attributed to {src}, which does not exist")
            problems += 1
            continue
        mine = os.path.join(EMITTER_DIR, base)
        if not os.path.exists(mine):
            print(f"note: {ref} has no copy at {rel(mine)}, where {src} writes; the "
                  "submitted file cannot be compared against a rendered one")
            continue
        if open(mine, "rb").read() != open(target, "rb").read():
            print(f"FAIL: {ref} differs from {rel(mine)}, the file {src} writes, so the "
                  "submitted figure is not that renderer's current output; copy it "
                  "across, or re-render if the copy is the stale one")
            problems += 1
    print(f"figure assets: {len(found)} included, {problems} problem(s)")
    return problems


if __name__ == "__main__":
    sys.exit(min(main(), 250))
