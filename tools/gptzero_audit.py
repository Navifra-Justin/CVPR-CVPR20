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
PAPER = ROOT / "paper"
OUT = ROOT / ".ai-audit"
RAW = OUT / "gptzero_raw.json"
REPORT = ROOT / "AI_WRITING_AUDIT.md"

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

def visible(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\(?:ref|cite|label|eqref|begin|end|section|subsection|subsubsection|paragraph|texttt|emph|textbf|footnote)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+(?:\[[^]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"\$[^$]*\$|\\\([^)]*\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ~,.:;")

def source_chunks():
    chunks = []
    for path in sorted(ROOT.rglob("*.tex")):
        if any(part in {".git", ".ai-audit", "build"} for part in path.parts):
            continue
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
                chunks.append(dict(file=str(path.relative_to(ROOT)), start=start,
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

def report(chunks, gz):
    findings = []
    for c in chunks:
        for s in sentences(c):
            flags = local_flags(s)
            if not flags: continue
            strong = any(x in flags for x in ["explanatory meta-sentence", "generic significance claim", "unsupported evaluative wording", "vague technical claim"])
            classification = "REWRITE" if strong else "REVIEW"
            findings.append({"classification": classification, "file": c["file"], "start": c["start"], "end": c["end"], "section": c["section"], "sentence": s, "reasons": flags})
    findings.sort(key=lambda x: (x["classification"] != "REWRITE", -len(x["sentence"])))
    residue = []
    for p in [ROOT / "paper", ROOT / "src", ROOT / "docs"]:
        if not p.exists(): continue
        for f in p.rglob("*"):
            if not f.is_file() or f.suffix in {".pdf", ".json", ".npz", ".log"}: continue
            try: t = f.read_text(errors="ignore")
            except Exception: continue
            for term in RESIDUE:
                if re.search(re.escape(term), t, re.I): residue.append((str(f.relative_to(ROOT)), term))
    flagged = {(x["file"], x["sentence"]) for x in findings}
    total_sentences = sum(len(sentences(c)) for c in chunks)
    counts = {"SAFE": max(0, total_sentences - len(flagged)),
              "REVIEW": sum(x["classification"] == "REVIEW" for x in findings),
              "REWRITE": sum(x["classification"] == "REWRITE" for x in findings)}
    claude = claude_status()
    out = ["# AI Writing Audit (first pass)", "", "This report is diagnostic only. No manuscript source was edited.", "",
           f"GPTZero status: **{gz['status']}**" + (f" ({gz.get('reason')})" if gz.get('reason') else ""),
           f"Claude status: **{claude}**; no external Claude assessment is claimed unless an Anthropic review is run.", "",
           "## Summary", "", f"- Extracted prose chunks: {len(chunks)}", f"- SAFE passages: {counts['SAFE']} (unflagged; not a proof of human authorship)", f"- REVIEW passages: {counts['REVIEW']}", f"- REWRITE passages: {counts['REWRITE']}", "- GPTZero confidence: unavailable because the API key is not configured.", ""]
    out += ["## Classification policy", "", "A GPTZero flag alone would not trigger a rewrite. In this keyless first pass, REVIEW/REWRITE labels are independent local writing-quality signals and require author review before any edit.", ""]
    out += ["## Highest-priority passages", ""]
    for i, f in enumerate(findings[:20], 1):
        out += [f"### {i}. {f['classification']} — {f['section']}", f"- Source: `{f['file']}:{f['start']}-{f['end']}`", f"- Reasons: {', '.join(f['reasons'])}", f"- Exact sentence: {f['sentence']}", "- GPTZero signal: unavailable in this run", "- Claude independent assessment: unavailable; local assessment requires human confirmation", ""]
    out += ["## Repository residue scan", ""]
    if residue:
        for f, t in residue[:100]: out.append(f"- `{t}` in `{f}`")
    else: out.append("No requested residue terms found in scanned source directories.")
    out += ["", "## GPTZero raw-response location", "", f"`{RAW.relative_to(ROOT)}`", ""]
    REPORT.write_text("\n".join(out) + "\n")
    return findings, counts

def main():
    OUT.mkdir(exist_ok=True)
    chunks = source_chunks()
    gz = gptzero(chunks)
    RAW.write_text(json.dumps(gz, indent=2, ensure_ascii=False))
    findings, counts = report(chunks, gz)
    print(json.dumps({"report": str(REPORT), "raw": str(RAW), "chunks": len(chunks), "counts": counts}, indent=2))

if __name__ == "__main__": main()
