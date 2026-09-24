"""197-item checklist style gate over the manuscript sources.

Each rule maps to a numbered checklist item.  Output is FILE:LINE  ITEM  evidence.
Comment lines and math-only lines are skipped where a rule would false-positive.
"""
import re, sys, os

FILES = sys.argv[1:] or ['paper/main.tex', 'paper/supplement.tex']

RULES = [
 # (item, label, regex, flags)
 ('25',  'semicolon',                r';(?!\s*$)'),
 ('26',  'em-dash',                  r'---'),
 ('27',  'colon-as-drama',           r'\b(is|are|was|were) this:'),
 ('28',  'i.e./e.g. overuse',        r'\b(i\.e\.|e\.g\.)'),
 ('30',  'raw double quote',         r'(?<![A-Za-z\\])"'),
 ('24',  'absolute word',            r'\b(always|never|all cases|every case|completely|entirely|impossible|guarantee[sd]?)\b'),
 ('54',  'nominalization stack',     r'\b\w+tion of the \w+tion\b'),
 ('55',  'number-percent spacing',   r'\d(?<!\\,)\\%'),
 ('56',  'British spelling',         r'\b(centre|behaviour|colour|analyse[sd]?|modelling|normalise\w*|generalise\w*|favour\w*|labelled|labelling|utilise\w*)\b'),
 ('59',  'lab-notebook phrasing',    r'\b(we (tried|ran into|noticed|realized|realised)|it turned out|at first we|initially we)\b'),
 ('63',  'promotional adjective',    r'\b(novel|powerful|remarkable|striking|surprisingly|dramatic\w*|significantly better|state[- ]of[- ]the[- ]art results|extensive experiments)\b'),
 ('65',  'presentation register',    r'\b(as we (will )?see|let us|let\'s|in this talk|note that,? importantly)\b'),
 ('66',  'meta-narration',           r'(^|\.\s+)(Finding|Rationale|Takeaway|Observation|Remark)[:.]|\b(We therefore|Three points follow|A natural objection|Two things follow|The upshot)\b'),
 ('68',  'open confession',          r'\b(unfortunately|we failed|we were unable|a weakness of|we admit|regrettably)\b'),
 ('188', 'rhetorical contrast',      r'\bnot\s+(a|an|the|merely|simply|just|only)?\s*\w+[, ]+but\s+(rather\s+)?(a|an|the)\b|\bwhat\s+\w+\s+(buys|costs)\b'),
 ('189', 'explanatory meta-sentence',r'\bThe (point|reason|idea|intuition|question) (here )?is\b|\bWhat (this|that) means is\b'),
 ('190', 'anthropomorphism',         r'\bthe (model|network|detector|method)\s+(knows|believes|wants|decides to|tries to|thinks|cares)\b'),
 ('191', 'metaphor',                 r'\b(load[- ]bearing|closes? the gap|carr(y|ies|ied) the gain|pays? off|under the hood|the heavy lifting|sheds light|a (double|two)[- ]edged)\b'),
 ('194', 'AI cadence: underscores',  r'\bThis (finding|result|observation) (underscores|highlights|demonstrates|suggests that|reveals)\b'),
 ('195', 'generic significance',     r'\b(plays? a (crucial|key|vital|important) role|is of (great|critical) importance|opens? (up )?new (avenues|possibilities)|paves? the way)\b'),
 ('196', 'empty closing summary',    r'\bIn summary, (we|this)\b|\bTaken together, (these|the)\b|\bOverall, (these|the) results\b'),
 ('197', 'exaggerated adverb',       r'\b(vastly|tremendously|extremely|incredibly|drastically|massively|substantially better)\b'),
]

def strip(line):
    s = re.sub(r'(?<!\\)%.*$', '', line)          # LaTeX comments
    s = re.sub(r'\$[^$]*\$', ' MATH ', s)          # inline math
    s = re.sub(r'\\cite[a-z]*\{[^}]*\}', ' CITE ', s)
    s = re.sub(r'\\(label|ref|eqref|input|include|newcommand|usepackage)\{[^}]*\}', ' REF ', s)
    return s

hits = 0
for f in FILES:
    if not os.path.exists(f): continue
    for n, raw in enumerate(open(f, encoding='utf-8'), 1):
        s = strip(raw)
        if not s.strip(): continue
        for item, label, rx in RULES:
            m = re.search(rx, s, re.I if item in ('56','63','65','68','197') else 0)
            if m:
                hits += 1
                print(f'{f}:{n}  [{item}] {label}  ->  {m.group(0)[:60]!r}')
print(f'\nTOTAL {hits} hit(s) over {len(FILES)} file(s)')
