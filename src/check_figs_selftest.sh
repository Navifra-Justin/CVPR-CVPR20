#!/usr/bin/env bash
# Exercise every branch of src/check_figs.py.  A checker that has never been shown to
# fail is not evidence: the branch that matters is the one nobody has seen fire.
# Everything happens in a temporary directory; this script writes nothing in the
# repository and never runs the checker against the live submission except in case 1,
# where a pass is the expected answer.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$(pwd)"
CHK="$ROOT/src/check_figs.py"
SUB="$ROOT/submission_2027/paper/latex"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
fails=0

chk () {  # chk <want-exit> <needle> <label> -- <cmd...>
  local want="$1" needle="$2" label="$3"; shift 4
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" != "$want" ] || ! printf '%s' "$out" | grep -q -- "$needle"; then
    echo "SELFTEST FAIL [$label]: exit $rc (wanted $want), output:"
    printf '%s\n' "$out" | sed 's/^/    /'
    fails=$((fails+1))
  else
    echo "ok   $label"
  fi
}

# 1. the live submission, which is expected to be complete and in sync
chk 0 "9 included, 0 problem" "live submission passes" -- python3 "$CHK"

# A writable copy of the paper directory for the failure cases.
cp -r "$SUB" "$T/latex"

# 2. an included figure that is not there: the fallback box case
rm "$T/latex/figs/chunkpos.pdf"
chk 1 "asset not yet rendered" "missing asset is reported" -- \
  env PAPER_DIR="$T/latex" python3 "$CHK"
cp "$SUB/figs/chunkpos.pdf" "$T/latex/figs/chunkpos.pdf"

# 3. a figure whose bytes are not the renderer's output
printf '%% drifted\n' >> "$T/latex/figs/chunkpos.pdf"
chk 1 "differs from paper/figs/chunkpos.pdf" "drifted asset is reported" -- \
  env PAPER_DIR="$T/latex" python3 "$CHK"
cp "$SUB/figs/chunkpos.pdf" "$T/latex/figs/chunkpos.pdf"

# 4. an included figure no script is known to render
cp "$SUB/figs/chunkpos.pdf" "$T/latex/figs/unclaimed.pdf"
printf '\\figasset{figs/unclaimed.pdf}{0.4\\linewidth}\n' > "$T/latex/zzextra.tex"
chk 1 "no known script renders" "unattributed asset is reported" -- \
  env PAPER_DIR="$T/latex" python3 "$CHK"
rm "$T/latex/zzextra.tex" "$T/latex/figs/unclaimed.pdf"

# 5. a paper directory that uses no \figasset at all: nothing verified, and the checker
#    must say so rather than print a clean bill for zero checks
mkdir -p "$T/empty"; printf 'nothing here\n' > "$T/empty/main.tex"
chk 1 "nothing was verified" "no figasset call is reported" -- \
  env PAPER_DIR="$T/empty" python3 "$CHK"

# 6. a paper directory that does not exist
chk 1 "is not a directory" "absent paper directory is reported" -- \
  env PAPER_DIR="$T/nowhere" python3 "$CHK"

# 7. the renderer a figure is attributed to is gone.  The checker derives its root from
#    its own location, so it is copied into a bare tree where src/make_figs.py is absent.
mkdir -p "$T/bare/src"
cp "$CHK" "$T/bare/src/check_figs.py"
# The exit status is the problem count, so all nine assets losing their renderer is
# exit 9; asserting 1 here would have been asserting the wrong contract.
chk 9 "which does not exist" "absent renderer is reported" -- \
  env PAPER_DIR="$T/latex" python3 "$T/bare/src/check_figs.py"

# 8. no rendered copy to compare against: a note, not a failure, since an archived
#    submission legitimately has no paper/figs/ beside it
mkdir -p "$T/bare2/src" "$T/bare2/paper/figs"
cp "$CHK" "$T/bare2/src/check_figs.py"
for s in make_figs.py e58f_fig.py e60_fig.py make_fig_qualitative.py make_fig_real.py; do
  : > "$T/bare2/src/$s"
done
chk 0 "has no copy at paper/figs" "uncomparable asset is a note" -- \
  env PAPER_DIR="$T/latex" python3 "$T/bare2/src/check_figs.py"

if [ "$fails" -ne 0 ]; then
  echo "check_figs selftest: $fails branch(es) did not behave as specified"
  exit 1
fi
echo "check_figs selftest: all branches behaved as specified"
