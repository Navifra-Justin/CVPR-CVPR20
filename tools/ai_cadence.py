"""AI-Style Gate statistics: sentence-cadence uniformity, opener repetition,
three-part parallelism, and LLM vocabulary over-use, on the visible prose.

With no arguments it reads the shipping manuscript, resolved from this file's own
location rather than from the caller's working directory: a relative default makes
the same command measure a different document -- or none -- depending on where it
is run, and this tool used to die in statistics.mean() on an empty population
instead of saying that it had read nothing.
"""
import os, re, sys, collections, statistics as st

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.environ.get('PAPER_DIR') or os.path.join(REPO, 'submission_2027/paper/latex')
if not os.path.isabs(PAPER_DIR):
    PAPER_DIR = os.path.join(REPO, PAPER_DIR)

def visible(t):
    t = re.sub(r'(?<!\\)%.*', '', t)
    t = re.sub(r'\\begin\{(figure|table|equation|align|tabular|thebibliography)\*?\}.*?\\end\{\1\*?\}', ' ', t, flags=re.S)
    t = re.sub(r'\$[^$]*\$', ' 0 ', t)
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?', ' ', t)
    return re.sub(r'[{}~\\]', ' ', t)

FILES = sys.argv[1:] or [os.path.join(PAPER_DIR, 'main.tex'),
                         os.path.join(PAPER_DIR, 'supp.tex')]
missing = [f for f in FILES if not os.path.exists(f)]
if missing:
    sys.exit('ai_cadence: missing manuscript source(s): ' + ', '.join(missing) +
             '; a source that cannot be opened is not a document with no problems')
txt = ' '.join(visible(open(f, encoding='utf-8').read()) for f in FILES)
# protect abbreviations so they do not create spurious sentence starts, which would
# inflate the opener-repetition counts below
for _a in ('Sec', 'Secs', 'Eq', 'Eqs', 'Fig', 'Figs', 'Tab', 'Tabs', 'Ref', 'Refs',
           'Alg', 'App', 'vs', 'cf', 'al', 'approx', 'No', 'Nos'):
    txt = txt.replace(_a + '.', _a + '\x00')
for _a in ('e.g.', 'i.e.'):
    txt = txt.replace(_a, _a.replace('.', '\x00'))
sents = [s.strip() for s in re.split(r'(?<=[.?!])\s+', txt) if len(s.split()) >= 4]
sents = [s.replace('\x00', '.') for s in sents]
lens = [len(s.split()) for s in sents]
# An empty population is a failure of the input, not a clean cadence report. The
# previous version reached statistics.mean([]) and died with a StatisticsError that
# said nothing about which files had been read.
print(f'files examined: {len(FILES)} -> ' + ', '.join(FILES))
if not sents:
    sys.exit(f'ai_cadence: 0 sentences extracted from {len(FILES)} file(s) '
             f'({", ".join(FILES)}); nothing was measured, and an empty population '
             'must not become a clean verdict')
print(f'sentences {len(sents)}  mean {st.mean(lens):.1f}  sd {st.pstdev(lens):.1f}  '
      f'cv {st.pstdev(lens)/st.mean(lens):.2f}  min {min(lens)}  max {max(lens)}')
print(f'  short(<12w) {sum(l<12 for l in lens)}  mid {sum(12<=l<=28 for l in lens)}  long(>28w) {sum(l>28 for l in lens)}')

op = collections.Counter(' '.join(s.split()[:2]).lower().strip('.,') for s in sents)
print('\ntop sentence openers (>=12 = cadence flag):')
for k, v in op.most_common(8):
    print(f'  {v:3d}  {k}{"   <-- FLAG" if v >= 12 else ""}')

par = [s for s in sents if re.search(r'\b\w+, \w+[^,]*, and \w+', s)]
print(f'\nthree-part parallel lists: {len(par)}  ({100*len(par)/len(sents):.1f}% of sentences; >15% = flag)')

LLMV = ['delve','intricate','nuanced','pivotal','realm','underscore','showcase','leverage',
        'robustly','seamless','holistic','paradigm shift','testament','landscape','tapestry',
        'crucial','comprehensive','meticulous','notably','importantly','furthermore','moreover']
low = txt.lower()
hits = [(w, len(re.findall(r'\b'+w+r'\w*\b', low))) for w in LLMV]
hits = [(w, n) for w, n in hits if n]
print('\nLLM-vocabulary counts:', hits or 'none')
tot = sum(n for _, n in hits)
print(f'  total {tot} over {len(txt.split())} words = {1000*tot/max(1,len(txt.split())):.2f} per 1000 (>2.0 = flag)')
