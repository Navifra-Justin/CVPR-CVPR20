# 논문 최종 점검 체크리스트 197 (2026-09-02 사용자 갱신본 — 현행 기준)

이 파일이 현행 기준이다. CVPR16의 사본은 이전 판이며 참조용으로만 남긴다.

## 상위 작업 프로토콜 — 실험 실패 시 반드시 이 순서로 (12단계)

1. 지는 결과 또는 부정적 결과 발견
2. 코드 작성이 제대로 되었는지 확인 (전체)
3. 부분적으로 확인 — 평가 또는 단순 계산 처리
4. 수정 후 이득 확인
5. 여전히 부정적이면 데이터 처리가 잘못되었는지 확인
6. 데이터 자체가 해당 기법과 맞지 않는지 확인
7. 평가 방법이 비대칭적인지 확인
8. 해당 기법에만 불리한 평가 방법인지 확인
9. 평가 메서드 변경
10. 기술의 차원을 1에서 2 또는 3차원으로 변경
11. 새로운 메서드 추가
12. 이 과정을 반복하여 유리하게 나오도록 진행

**유리하게 나오는 방법은 반드시 존재한다.**

---

## A. 논문 전체 spine / 핵심 주장
1. 한 문장으로 줄였을 때 강한 메시지가 나오는가
2. 첫 3문장 안에 문제가 보이는가
3. 첫 1페이지 안에 핵심 기여가 보이는가
4. 논문의 정체성이 긍정문으로 정의되는가
5. contribution이 method trick이 아니라 문제 구조와 연결되는가

## B. 독자 이해 흐름
6. 독자가 이미 안다고 가정하지 않았는가
7. 독자의 질문 순서대로 글이 진행되는가
8. 새 개념은 필요성이 설명된 뒤 등장하는가
9. 방법 이름보다 실패 원인을 먼저 말하는가
10. 각 문단이 하나의 역할만 수행하는가
11. 문단 끝이 다음 문단의 질문을 만드는가
12. 추상어 뒤에 물리적 예시가 붙는가

## C. Abstract / Introduction 구조
13. Abstract 첫 문장은 배경 또는 문제로 시작하는가
14. Abstract에 숫자가 너무 많지 않은가 (대표 2–4개)
15. Abstract에서 서로 다른 metric regime이 섞이지 않았는가
16. Abstract에 mechanism 하나와 main result 하나가 분명한가
17. Introduction 첫 페이지가 너무 빠르게 고차원 주장으로 가지 않는가
18. Contribution 앞에 2–3문장 bridge가 있는가
19. Contribution bullet이 간결하고 병렬적인가
20. Contribution에 세부 수치가 과하지 않은가

## D. 주장과 용어의 정확성
21. 핵심 용어가 operational definition을 갖는가
22. 주장하는 것과 주장하지 않는 것이 분명한가
23. claim 강도와 evidence 강도가 맞는가
24. every, all, only, must, cannot을 남발하지 않았는가
25. first claim이 과하지 않은가
26. 강한 단어가 근거와 붙어 있는가
27. 부정문으로만 논문 가치를 설명하지 않았는가

## E. 실험 설계와 방어력
28. 가장 자연스러운 반론을 먼저 막았는가
29. 단순 baseline과 강한 baseline을 모두 비교했는가
30. negative result가 논문 논리를 떠받치는가
31. external reference가 있는가
32. cross-dataset 또는 cross-backbone 검증이 있는가
33. metric이 practical meaning과 연결되는가
34. 서로 다른 실험 숫자의 의미를 안내했는가
35. 실험 결과가 claim 순서와 같은 순서로 제시되는가
36. limitation이 boundary로 정리되었는가, 아니면 제거되었는가

## F. Related Work / Section heading
37. Related work heading이 중립적인 명사구인가
38. Heading에 설명문이나 슬로건이 들어가지 않았는가
39. Related work는 카테고리 → 기존 작업 → 차이 순서인가
40. 경쟁 방법 차이를 과하게 방어적으로 쓰지 않았는가

## G. 문장 길이와 가독성
41. 35단어 이상 문장을 점검했는가
42. 한 문장에 contrast가 2개 이상 들어가지 않았는가
43. `;`, `—`, `:`가 과도하게 쓰이지 않았는가
44. `i.e.`가 정확히 쓰였는가
45. 대명사 this, it, which의 지시 대상이 명확한가

## H. 괄호 / 따옴표 / 삽입구
46. 괄호 안에 핵심 주장을 넣지 않았는가
47. 한 문단에 괄호가 너무 많지 않은가
48. Raw double quotes를 쓰지 않았는가
49. 괄호를 지워도 논리가 유지되는가
50. 구어체/발표체 표현을 검색해서 제거했는가
    (`because`, `This is not`, `We do not`, `The point is`, `The reason`, `cleanly`,
    `curiosity`, `sacrifice`, `price`, `every`, `all`, `only`, `must`, `cannot`,
    `i.e.`, `;`, `—`, `"`, `Why no`)

51. 8장 장수 제한
52. 단점이나 한계는 최소화 또는 제거, 강점은 강조
53. 몇 개 경우에서만 검증해도 일반화되었다고 서술 (데이터셋 2~4개 검증 후 일반화 주장은 표준 관행)
54. 부자연스러운 명사형(Directional Unsafety 등) 확인·변경
55. 숫자–% 간 공백 확인
56. 영국식–미국식 영어 혼재 지양
57. 섹션 간 내용 모순 검토
58. 연구노트식 표현(Earlier mini run 등) 지양
59. Figure 내부 글씨 겹침·가독성 검사
60. 내부 용어 통일
61. 문장 구분 없는 세미콜론 삭제
62. 강점은 강조, 단점·한계는 최소화 또는 제거
63. 학술적 어투 유지, 홍보톤·발표톤 확인
64. 메타 문장 금지 (Finding, Rationale, Mechanism, We therefore, Three points follow,
    A natural objection, This is what makes...)
65. 발표체 문체·문맥 부자연스러움 제거
66. 슬라이드·rebuttal·구두설명 같은 문장 금지
67. 영국식 어투 금지, 미국식 검증
68. 미국식·학술식 어투, 문단 앞뒤 확인
69. 열린 자백 금지
70. 상위권 학술 논문 본문처럼 비개입적으로 읽히는가

71. Falsifiable Thesis Test
72. Final-Objective Alignment
73. Nearest-Alternative Delta
74. Alternative-Explanation Kill Test
75. Claim–Evidence Ledger
76. Validity Envelope
77. Claim Fragility Test
78. Quality–Cost Pareto Test
79. SOTA-Independent Value Test
80. Bounded Limitation Test
81. Paradigm-Delta Test
82. Method Compression Test
83. Hard-Case-First Evidence
84. Cross-Task Reuse Test
85. Reviewer Memory Test
86. Field-Consequence Test
87. 방어 문구 금지, 강점 강조
88. Technical Identity Test — 어떤 기술로 어떤 문제를 푸는 논문인지 초록에서 즉시 보이는가
89. Core Contribution Singularization Test — 가장 중요한 기여가 한 문장으로 압축되는가
90. Contribution Hierarchy Test — 핵심/보조/구현의 위계가 분명한가
91. Technical Base Declaration Test — 어떤 기존 기술 위에 세워졌는지 초반에 명시되는가
92. Parent-Method Delta Test — Retained / Modified / Removed가 분리되는가
93. Nearest-Alternative Delta Test II — 차이가 연산 수준에서 설명되는가
94. Mechanism Reconstruction Test — 독자가 파이프라인을 재구성할 수 있는가
95. Input–Operation–Output Test — 모든 핵심 모듈의 입력·연산·출력이 구체적인가
96. Representation Definition Test — 핵심 표현의 실체가 정의되는가
97. Algorithmic Specificity Test — 재현에 필요한 핵심 정보가 본문에 있는가
98. Name Necessity Test — 새 용어가 정말 필요한가
99. Name-to-Substance Test — 이름이 실체보다 거창하지 않은가
100. One-Concept-One-Name Test — 같은 개념을 여러 이름으로 부르지 않는가
101. Definition-before-Usage Test — 정의 전에 용어를 쓰지 않는가
102. Problem–Mechanism Correspondence Test
103. Component Causality Test — causal ablation이 있는가
104. Vanilla-Parent Baseline Test — 기반 방법 그대로의 비교가 있는가
105. Controlled-Comparison Test — 변경된 요소가 하나인가
106. Assumption Contract Test — 요구 가정이 명시되는가
107. Assumption-to-Deployment Closure Test
108. Operating-Range Test
109. Core-Figure Alignment Test — 핵심 그림이 핵심 기여를 보여주는가
110. Visual Mechanism Test
111. Figure–Text Priority Consistency Test
112. Main-Result Attribution Test
113. Baseline Relevance Test
114. Ablation-to-Claim Alignment Test
115. Intermediate-Evidence Test
116. "So What Exactly Changed?" Test
117. 30-Second Method Sketch Test
118. Reviewer "Why?" Test
119. Reviewer "How?" Test
120. Reviewer "Isn't This Existing?" Test
121. Novelty Attribution Test — 무엇이 새롭고 무엇이 조합인지 구분되는가
122. Complexity Justification Test
123. Technical Density Balance Test
124. Result-to-Mechanism Traceability Test
125. Abstract Mechanism Completeness Test
126. Abstract Result Dependency Test
127. Evidence Granularity Test
128. Failure-Mode Evidence Test
129. Hard-Case Mechanism Match Test
130. Reader-Inference Burden Test
131. Section Self-Containment Test
132. Figure Caption Sufficiency Test
133. Terminology Load Test
134. Contribution-to-Figure-to-Experiment Mapping Test
135. First-Page Technical Completeness Test
136. No-Decorative-Complexity Test
137. Native Academic Naturalness Test
138. Native Collocation Test
139. Information-Flow Test — known information → new information
140. Sentence-to-Sentence Causality Test
141. Concrete-Verb Test — facilitate/enable/leverage/utilize가 실제 연산을 숨기지 않는가
142. Nominalization Density Test — -tion/-ment/-ity/-ness/-ance/-ence가 한 문장에 3개 이상인가
143. Academic Phrase Authenticity Test
144. Over-Polishing Test — 수정 후 더 길고 추상적이 되지 않았는가
145. Translationese Test
146. Paragraph Rhythm Test — 같은 주어·구조 3회 이상 반복 금지
147. Pronoun and Reference Naturalness Test
148. One-Read Comprehension Test
149. Read-Aloud Test
150. 어색하지 않으면 수정하지 말 것, 어색하면 최소 수정
151. 그림·동영상 글씨는 Times New Roman

## 추가 논문 구조 / Narrative Architecture 원칙
152. Single Central Thesis Test
153. First-Time Reviewer Reconstruction Test
154. Architecture-Before-Rewrite Test — Diagnosis → Thesis → Story → Section Structure → Evidence Mapping → Rewrite
155. Existing-Structure Non-Constraint Test
156. Question-Driven Section Order Test
157. Single Narrative Backbone Test
158. Main-Finding Prominence Test
159. Failure-Before-Method Test
160. Figure/Table Claim Necessity Test
161. Novelty-by-Experimental-Design Test — novelty가 문장이 아니라 실험 설계에서 드러나는가
162. Claim–Evidence Proportionality Test II
163. Evidence Hierarchy Test — Existence / Discrimination / Diagnosis / Intervention / Attribution / Generalization / Boundary
164. Seven-Question Paper Reconstruction Test — Problem / Gap / Insight / Method / Evidence / Generality / Limitation
165. Scientific-Argument-Over-Manuscript-Preservation Rule

## L. 실제 CVPR 채택 논문 분석 기반 원칙
기준 논문: Generative Image Dynamics (CVPR 2024 Best Paper), MVBench (CVPR 2024 Highlight),
Learning Object State Changes in Videos (CVPR 2024), Neuralangelo (CVPR 2023),
Time Blindness (CVPR 2026), AbstainEQA (CVPR 2026 Highlight), VirtueBench (CVPR 2026),
SEASON (CVPR 2026).

166. One-Axis Reframing Test — Existing setting assumes X; we instead evaluate/model Y
167. Figure-1-as-Paper Test
168. Contrast-Before-Acronym Rule
169. Two-or-Three-Kernel Memory Test
170. Headline-Result Test
171. Human-or-Oracle Anchor Test
172. Paired-Evidence Test
173. Shortcut-Exclusion Test
174. Metric-Follows-Failure Rule
175. Benchmark-Is-a-Test-Not-a-Collection Rule
176. Taxonomy-Origin Test
177. Main-Table-as-Thesis Test
178. Breadth-After-Effect Rule
179. Mechanism-to-Ablation Isomorphism Test
180. Representation-Justification Test
181. Application-Is-Consequence Rule
182. Failure-Scale Separation Test
183. Natural-Progression Test
184. Evidence-Density Pacing Test
185. Reviewer-Reconstruction-from-Figures Test
186. Accepted-Paper Triangulation Rule — 최소 3종류의 기준 논문으로 교차검증
187. Naturalness Meta-Gate — 모든 내용이 "여기에 있어야 하는 이유"를 갖는가

## 최종 Critical Gate (G1–G12)
- G1. Technical Identity — 첫 3–5문장으로 어떤 기술 논문인지 안다
- G2. Core Contribution — 가장 중요한 기술적 기여를 한 문장으로 말할 수 있다
- G3. Parent Delta — 유지·제거·변경이 명확하다
- G4. Mechanism — 핵심 방법이 무엇을 계산하는지 설명할 수 있다
- G5. Naming — 새 용어가 모두 필요하다
- G6. Causality — 어떤 component가 어떤 failure를 해결하는지 대응된다
- G7. Direct Baseline — 가장 가까운 기존 방법과 직접 비교가 있다
- G8. Assumption — 요구 조건과 실제 적용 조건의 관계가 설명된다
- G9. Visual Evidence — 핵심 기여가 Figure에서 가장 강하게 보인다
- G10. Attribution — 성능 향상의 출처가 실험으로 추적된다
- G11. Reconstructability — Method만 읽고 input→output을 그릴 수 있다
- G12. Reviewer Memory — 문제·핵심 아이디어·차이·대표 결과가 기억된다

## 추가 Academic Writing / LLM-Style 제거 (188–197)
188. Rhetorical Contrast Elimination Test — `not X but Y`, `what X buys/costs` 제거
189. Explanatory Meta-Sentence Removal Test — `What this tells us is`, `Two things make this possible` 제거
190. Technical Agency Test — 의인화 금지 (the model sees / the graph knows)
191. Metaphorical Technical Language Test — load-bearing, closes the gap, carries the gain 등 제거
192. Evidence-Calibrated Claim Test
193. Technical Heading Test — heading은 중립적 technical noun phrase
194. Syntactic Repetition Test
195. Result Reinterpretation Redundancy Test
196. Condition–Method–Observation–Interpretation Test
197. Precision-over-Rhetoric Meta-Gate

## 추가 문체 Critical Gate (S1–S10)
- S1 Rhetorical Contrast · S2 Meta Explanation · S3 No Anthropomorphism · S4 No Metaphor
- S5 Claim Calibration · S6 Technical Headings · S7 Syntax Variety · S8 Result Economy
- S9 Evidence First · S10 Precision First

> **"똑똑하게 들리게 쓰지 말고, 정확하게 쓴다."**

## 반드시 필수 확인 규칙
- 기준 논문을 **외부에서 직접 가져와** 정하고, 문체·구조·그림을 그것에 비추어 평가한다.
  내부 논문은 기준이 될 수 없다. 어떤 기준 논문을 썼고 무엇을 참고했는지 함께 보고한다.
- CVPR 2024–2026의 가장 유사한 accepted paper와 공식 reviewer 기준으로 상대평가하여
  **Reject / Borderline / Accept / Strong Accept** 중 하나로 판정한다.
  accept를 막는 Critical/Major가 있으면 수정하고 체크리스트를 다시 돌린다.
- 문장은 대안이 있다는 이유만으로 고치지 않는다. 문법과 자연스러움을 따로 판정하고,
  이미 자연스러운 문장은 보존하며, 고칠 때는 최소한으로 고친다.
  문단은 문장 단위 판단 전에 통독하여 논리 흐름과 정보 순서의 어색함을 먼저 본다.
