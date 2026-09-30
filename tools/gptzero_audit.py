#!/usr/bin/env python3
"""First-pass writing audit for the CVPR manuscript.

The script keeps source locations for prose chunks, sends paragraph-sized chunks
to GPTZero when GPTZERO_API_KEY is available, and writes a local audit report.
It deliberately does not edit manuscript files.  Claude is an optional second
reviewer when ANTHROPIC_API_KEY is configured; no Claude assessment is invented
when that key is absent.
"""
from __future__ import annotations

import json, os, re, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The live submission is submission_2027/paper/latex; the top-level paper/
# tree is a stale draft.  The residue scan used to classify the draft as "the
# files that ship".  PAPER_DIR overrides the directory for testing.
PAPER = Path(os.environ.get("PAPER_DIR", "submission_2027/paper/latex"))
if not PAPER.is_absolute():
    PAPER = ROOT / PAPER
# The prose population used to be ROOT.rglob("*.tex"), which swept the stale
# top-level paper/ draft in alongside the submission: 194 of 404 chunks, and
# highest-priority passages quoted from a file that is not submitted.  The
# population is now the shipping directory alone.
SCAN_DIRS = [PAPER, ROOT / "src", ROOT / "docs"]
OUT = Path(os.environ.get("AUDIT_OUT") or (ROOT / ".ai-audit"))
RAW = OUT / "gptzero_raw.json"
REPORT = Path(os.environ.get("AUDIT_REPORT") or (ROOT / "AI_WRITING_AUDIT.md"))

RESIDUE = ["Here is the revised", "Certainly", "As requested", "the provided text",
           "the revised version", "Here's", "AI language model", "prompt",
           "instruction", "rewrite", "placeholder"]
REWRITE_PATTERNS = [
    (r"\bwhat (this|the result) (tells|shows) us is\b", "explanatory meta-sentence"),
    (r"\bthe key point is\b|\bthis is important because\b", "explanatory meta-sentence"),
    (r"\bwhat (x|this) (buys|costs)\b", "rhetorical contrast"),
    (r"\bthis (clearly )?(demonstrates|confirms|highlights|underscores)\b", "generic significance claim"),
    (r"\bwe therefore\b|\bwe first\b|\bwe then\b|\bwe further\b", "formulaic transition"),
    (r"\b(the )?(right|correct) (signal|formulation)\b", "unsupported evaluative wording"),
]
REVIEW_PATTERNS = [
    (r"\bnot\b.*\bbut\b|\brather than\b", "rhetorical contrast"),
    (r"\b(can|does|will)\s+(?:never|always|only|not)\b|\b(all|none|every|must|cannot)\b", "absolute wording"),
    (r"\bfundamentally\b|\bcompelling\b|\bpivotal\b|\bcrucial\b|\bremarkable\b", "overstated adjective"),
    (r"\bThis (result|finding|observation)\b", "generic result transition"),
]

def rel_root(p: Path) -> str:
    """Display path, tolerant of an output location outside the repository."""
    try: return str(p.relative_to(ROOT))
    except ValueError: return str(p)


def visible(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\(?:ref|cite|label|eqref|begin|end|section|subsection|subsubsection|paragraph|texttt|emph|textbf|footnote)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+(?:\[[^]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"\$[^$]*\$|\\\([^)]*\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ~,.:;")

def manuscript_sources():
    """The .tex files that actually ship, named explicitly so the count is auditable."""
    if not PAPER.is_dir():
        sys.exit(f"gptzero_audit: {PAPER} is not a directory; no manuscript source "
                 "would be read, and a report over nothing is not a clean document")
    files = sorted(p for p in PAPER.glob("*.tex")
                   if not any(part in {".git", ".ai-audit", "build", "submission_package"}
                              for part in p.parts))
    if not files:
        sys.exit(f"gptzero_audit: no .tex under {PAPER}; the glob matched zero files, "
                 "so nothing was audited and an empty population must not become a "
                 "clean verdict")
    return files


def source_chunks(files):
    chunks = []
    for path in files:
        lines = path.read_text(errors="replace").splitlines()
        section = "Preamble"
        buf, start = [], None
        in_bib = False
        def flush(end):
            nonlocal buf, start
            if not buf or start is None: return
            raw = "\n".join(buf).strip()
            txt = visible(raw)
            if len(txt.split()) >= 8:
                chunks.append(dict(file=rel_root(path), start=start,
                                   end=end, section=section, text=txt, raw=raw))
            buf, start = [], None
        for i, line in enumerate(lines, 1):
            if "thebibliography" in line or "\\begin{thebibliography}" in line: in_bib = True
            if in_bib: continue
            m = re.search(r"\\(?:section|subsection|subsubsection|paragraph)\{([^}]*)\}", line)
            if m:
                flush(i - 1); section = re.sub(r"\\[A-Za-z]+", "", m.group(1)).strip()
            if not line.strip() or line.lstrip().startswith(("%", "\\begin{", "\\end{")):
                flush(i - 1); continue
            if start is None: start = i
            buf.append(line)
        flush(len(lines))
    return chunks

def sentences(chunk):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\$])", chunk["text"]) if len(s.split()) >= 8]

def local_flags(s):
    flags = []
    for pat, reason in REWRITE_PATTERNS + REVIEW_PATTERNS:
        if re.search(pat, s, re.I): flags.append(reason)
    words = s.split()
    if len(words) >= 40: flags.append("long sentence / modifier load")
    if sum(s.count(x) for x in ["(", "["]) >= 2: flags.append("dense parenthetical insertion")
    if s.count(",") >= 4: flags.append("comma-heavy sentence rhythm")
    return list(dict.fromkeys(flags))

def gptzero(chunks):
    key = os.environ.get("GPTZERO_API_KEY")
    if not key:
        return {"status": "not_run", "reason": "GPTZERO_API_KEY is not set", "results": []}
    results = []
    for c in chunks:
        payload = json.dumps({"document": c["text"]}).encode()
        req = urllib.request.Request("https://api.gptzero.me/v2/predict/text", data=payload,
            headers={"x-api-key": key, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as r: body = json.loads(r.read())
            results.append({"file": c["file"], "start": c["start"], "end": c["end"], "response": body})
        except Exception as e:
            results.append({"file": c["file"], "start": c["start"], "end": c["end"], "error": type(e).__name__ + ": " + str(e)})
    return {"status": "completed", "results": results}

def claude_status():
    return "configured but not called in the first pass" if os.environ.get("ANTHROPIC_API_KEY") else "not configured"

def report(chunks, gz, files):
    findings = []
    for c in chunks:
        for s in sentences(c):
            flags = local_flags(s)
            if not flags: continue
            strong = any(x in flags for x in ["explanatory meta-sentence", "generic significance claim", "unsupported evaluative wording", "vague technical claim"])
            classification = "REWRITE" if strong else "REVIEW"
            findings.append({"classification": classification, "file": c["file"], "start": c["start"], "end": c["end"], "section": c["section"], "sentence": s, "reasons": flags})
    findings.sort(key=lambda x: (x["classification"] != "REWRITE", -len(x["sentence"])))
    total_sentences = sum(len(sentences(c)) for c in chunks)
    residue, residue_repo = [], []
    scanned = 0            # files whose bytes were actually read
    unreadable = []
    missing = [str(p) for p in SCAN_DIRS if not p.exists()]
    if missing:
        # A directory that is not there used to be skipped in silence, which is how a
        # residue scan over nothing printed "No requested residue terms found".
        sys.exit("gptzero_audit: residue-scan directory missing: " + ", ".join(missing) +
                 "; an unread directory is not a directory with no residue")
    for p in SCAN_DIRS:
        for f in p.rglob("*"):
            if not f.is_file() or f.suffix in {".pdf", ".json", ".npz", ".log"}: continue
            try: t = f.read_text(errors="ignore")
            except Exception as e:
                unreadable.append((str(f), type(e).__name__)); continue
            scanned += 1
            ships = f.parent == PAPER and f.suffix == ".tex"
            for term in RESIDUE:
                if re.search(re.escape(term), t, re.I):
                    (residue if ships else residue_repo).append((rel_root(f), term))
    ship_scanned = sum(1 for f in PAPER.glob("*.tex"))
    if scanned == 0 or ship_scanned == 0:
        sys.exit(f"gptzero_audit: residue scan read {scanned} file(s), {ship_scanned} of them "
                 f"shipping .tex under {PAPER}; nothing was scanned and an empty population "
                 "must not become a clean verdict")
    if unreadable:
        sys.exit("gptzero_audit: unreadable input, so the scan is incomplete: " +
                 ", ".join(f"{f} ({e})" for f, e in unreadable))
    flagged = {(x["file"], x["sentence"]) for x in findings}
    counts = {"SAFE": max(0, total_sentences - len(flagged)),
              "REVIEW": sum(x["classification"] == "REVIEW" for x in findings),
              "REWRITE": sum(x["classification"] == "REWRITE" for x in findings)}
    claude = claude_status()
    out = ["# AI Writing Audit (first pass)", "", "This report is diagnostic only. No manuscript source was edited.", "",
           f"GPTZero status: **{gz['status']}**" + (f" ({gz.get('reason')})" if gz.get('reason') else ""),
           f"Claude status: **{claude}**; no external Claude assessment is claimed unless an Anthropic review is run.", "",
           "## Summary", "",
           f"- Manuscript sources read: {len(files)} — " + ", ".join(rel_root(f) for f in files),
           f"- Residue-scan files read: {scanned} ({ship_scanned} shipping `.tex`)",
           f"- Sentences examined: {total_sentences}",
           f"- Extracted prose chunks: {len(chunks)}", f"- SAFE passages: {counts['SAFE']} (unflagged; not a proof of human authorship)", f"- REVIEW passages: {counts['REVIEW']}", f"- REWRITE passages: {counts['REWRITE']}", "- GPTZero confidence: unavailable because the API key is not configured.", ""]
    out += ["## Classification policy", "", "A GPTZero flag alone would not trigger a rewrite. In this keyless first pass, REVIEW/REWRITE labels are independent local writing-quality signals and require author review before any edit.", ""]
    out += ["## Highest-priority passages", ""]
    for i, f in enumerate(findings[:20], 1):
        out += [f"### {i}. {f['classification']} — {f['section']}", f"- Source: `{f['file']}:{f['start']}-{f['end']}`", f"- Reasons: {', '.join(f['reasons'])}", f"- Exact sentence: {f['sentence']}", "- GPTZero signal: unavailable in this run", "- Claude independent assessment: unavailable; local assessment requires human confirmation", ""]
    out += ["## Residue scan", "",
            f"### Manuscript sources (`{rel_root(PAPER)}/*.tex`, the files that ship)", ""]
    if residue:
        for f, t in residue[:100]: out.append(f"- `{t}` in `{f}`")
    else: out.append("No requested residue terms found in the manuscript sources.")
    out += ["", "### Other scanned directories (`src/`, `docs/`; tooling and internal notes, not submitted)", ""]
    if residue_repo:
        for f, t in residue_repo[:100]: out.append(f"- `{t}` in `{f}`")
    else: out.append("No requested residue terms found.")
    out += ["", "## GPTZero raw-response location", "", f"`{rel_root(RAW)}`", ""]
    REPORT.write_text("\n".join(out) + "\n")
    return findings, counts

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = manuscript_sources()
    chunks = source_chunks(files)
    if not chunks:
        sys.exit(f"gptzero_audit: {len(files)} source(s) under {PAPER} yielded 0 prose "
                 "chunks; nothing was audited and an empty population must not become a "
                 "clean verdict")
    gz = gptzero(chunks)
    RAW.write_text(json.dumps(gz, indent=2, ensure_ascii=False))
    findings, counts = report(chunks, gz, files)
    print(json.dumps({"report": str(REPORT), "raw": str(RAW),
                      "paper_dir": str(PAPER),
                      "sources": [rel_root(f) for f in files],
                      "chunks": len(chunks),
                      "sentences": sum(len(sentences(c)) for c in chunks),
                      "counts": counts}, indent=2))

if __name__ == "__main__": main()
