# EVALUATION_DIMENSIONS.md
## A Framework for Capturing Technical Writing Voice

This document defines the analytical dimensions used to extract a writer's distinctive voice from a corpus of technical writing. It is designed primarily for scientific and academic writing but generalizes to any domain with mixed formal registers (papers, proposals, reviews, technical correspondence).

The goal is not to describe *good* writing in the abstract — it is to identify what makes *this writer's* writing recognizable as theirs. Dimensions that yield generic observations ("writes clearly," "uses technical terminology") should be discarded or refined until they carry diagnostic signal.

---

### How to use this document

In a batched extraction session, upload a set of documents and instruct Claude to analyze them against each dimension below, producing structured observations per dimension. Observations should always be **specific and falsifiable** — they should describe a pattern that another competent writer in the same field would *not* necessarily exhibit.

After all batches are processed, a synthesis session collapses per-batch observations into a final `SKILL.md` using the provided template.

**Before running any extraction session**, ensure your corpus is configured in `corpus.yaml` and run the two utility scripts in order:

```bash
python count_tokens.py --corpus corpus.yaml
python compute_weights.py --corpus corpus.yaml --output weights.txt
```

Inspect `weights.txt` before proceeding. If any document is dominating a dimension in a way that doesn't reflect your intentions, adjust `type_weights` or per-document `confidence` values in `corpus.yaml` before extracting. The weight table is your sanity check — use it.

**Accepted input formats:** PDF (`.pdf`) for all document types except technical email. Plaintext (`.txt`) for technical email, organized by thematic grouping (see Document Type Classification below).

---

## Document Type Classification

Every document uploaded for analysis must be classified before extraction begins. Classification determines which dimensions the document is most diagnostic for, guides batch composition, and drives the weighting system in `corpus.yaml`.

### The scaffold spectrum

Document types fall on a spectrum from most to least genre-constrained. Voice signal increases as scaffold decreases — the writer has fewer structural crutches to lean on and more discretionary choices to make:

```
Journal paper → Proposal → Review/perspective → Research statement → Letter of rec → Technical email
most constrained                                                               least constrained
lowest raw voice signal                                               highest raw voice signal
```

This spectrum has a practical implication: a small, high-confidence corpus of technical emails and research statements may carry more voice signal per token than a large corpus of co-authored journal papers. Token normalization and per-document confidence ratings in `corpus.yaml` are what make this tradeoff explicit and tunable.

### Document types

**Journal paper** — peer-reviewed empirical or review article. Heavily constrained by IMRaD conventions and journal style. Only upload papers where you have clear first-author editorial control. Co-authored papers where you wrote specific sections may be included but should receive lower confidence ratings.

**Proposal** — grant application narrative (specific aims, significance, innovation, approach, or equivalent). Discretionary structure with required advocacy register. High diagnostic value for epistemic stance, argumentation structure, and register modulation. Only upload proposals where you were PI or lead writer.

**Research statement** — career narrative document (for job applications, tenure, fellowship applications). Writer narrates their own intellectual trajectory with minimal genre scaffolding. High diagnostic value for semantic style and argumentation structure. Often the single highest-signal document in a corpus.

**Letter of recommendation** — written on behalf of another person. Almost no genre scaffolding; writer must characterize someone else's work in their own terms. High diagnostic value for transition logic and argumentation structure precisely because structural crutches are absent.

**Review article / perspective** — synthetic or opinion piece with discretionary organization. Intermediate between paper and proposal in constraint level. High diagnostic value for semantic style and organizational rhythm.

**Technical report / white paper** — institutional or project documentation. Variable constraint level. Flag the specific context (internal report, NASA deliverable, etc.) as it affects register expectations. Use `other` type in `corpus.yaml` with an explanatory note.

**Extended abstract / conference paper** — compressed format. Useful for syntax and vocabulary dimensions; less useful for large-scale organizational structure. Use `journal_paper` type in `corpus.yaml`.

**Technical email** — informal professional writing in `.txt` format. The lowest-scaffold document type: captures the reasoning style that operates when no genre conventions apply. High diagnostic value for transition logic, vocabulary, and as the floor anchor for register modulation. Organize into thematic groupings rather than individual threads, using the `sublabel` field in `corpus.yaml` to distinguish:

- `peer scientific discussion` — substantive exchanges with collaborators; highest raw voice signal
- `proposal and pitch discussion` — emails explaining research direction to program managers or collaborators
- `student and mentoring correspondence` — explanatory writing; high signal for semantic style and analogy use
- `other` — specify in notes

**Other** — specify the document type and constraint level explicitly in `corpus.yaml` notes before proceeding with extraction.

### Weighting system

The contribution of each document to the voice analysis is controlled by four factors that multiply together, then normalize per dimension:

```
effective_weight = (type_weight × confidence × temporal_weight × diagnostic_value) / prose_tokens
```

- **type_weight** — set globally in `corpus.yaml` under `type_weights`. Reflects your trust in each document *category* given your specific corpus situation. Increase `technical_email` to emphasize rawest personal style.
- **confidence** — set per document (1–5 scale). Reflects how representative this specific document is of your voice at its most characteristic. See `corpus.yaml` for scale definition.
- **temporal_weight** — set globally via `temporal.mode` in `corpus.yaml`. Either `uniform` (all periods equal) or `recency` (exponential decay by document age, tunable via `recency_halflife`).
- **diagnostic_value** — fixed by the Document Type Matrix below. Encodes how diagnostic each document type is for each dimension. Not user-tunable.
- **prose_tokens** — computed automatically by `count_tokens.py`. Normalizes for document length so high-volume document types do not drown out low-volume ones.

---

## Document Type Matrix

The matrix below indicates which dimensions each document type is most diagnostic for. **Primary** means the document type strongly reveals this dimension. **Secondary** means it offers useful signal but with caveats. Blank means the document type is too constrained or too variable to yield reliable signal for this dimension.

| Dimension | Journal paper | Proposal | Research statement | Letter of rec | Review / perspective | Correspondence |
|---|---|---|---|---|---|---|
| 1. Syntactic style | Primary | Secondary | Secondary | Secondary | Primary | Secondary |
| 2. Semantic style | Secondary | Primary | Primary | Secondary | Primary | |
| 3. Vocabulary | Primary | Primary | Primary | Secondary | Primary | Secondary |
| 4. Rhythm & cadence | Secondary | Primary | Primary | | Primary | |
| 5. Epistemic stance | Secondary | Primary | Primary | Secondary | Primary | |
| 6. Argumentation structure | | Primary | Primary | Primary | Primary | |
| 7. Transition logic | Secondary | Secondary | Secondary | Primary | Secondary | Primary |
| 8. Quantitative integration | Primary | Primary | | | Secondary | |
| 9. Register modulation | | | | | | |

**Note on Dimension 9 (Register modulation):** This dimension cannot be assessed from any single document type — it requires *comparison across* at least two document types from the same writer. It should be evaluated only during the synthesis step, after observations from multiple document types are available. The scaffold spectrum above defines the natural comparison axis: what invariants survive as constraints relax from journal paper to technical email?

### Recommended batch composition

Batch extraction sessions should be organized by document type rather than chronologically or by topic. Mixing document types within a batch makes it harder to flag which observations are type-specific vs. voice-invariant.

A minimum viable corpus for a complete analysis:
- At least 3 journal papers with clear first-author editorial control
- At least 1 proposal narrative (specific aims or significance section preferred)
- At least 1 research statement or review article
- At least 1 letter of recommendation, if available
- At least 1 technical email grouping, if available — even a modest volume here adds disproportionate signal given its position at the low-scaffold end of the spectrum

Chronological spread matters. Use `year` or `year_range` fields in `corpus.yaml` to record when each document was written. If voice evolution over time is a concern, enable `recency` mode in `corpus.yaml` rather than manually selecting recent-only documents — this preserves the full corpus while mathematically down-weighting older material.

---

## Dimension 1 — Syntactic Writing Style

**What it captures:** Sentence construction patterns at the grammatical level. Clause ordering, use of passive vs. active voice, subordination habits, punctuation as a structural tool, sentence length distribution.

**What to look for:**
- Does the writer favor front-loaded or end-loaded sentences? (Does the main claim come first, or does evidence build toward it?)
- How is passive voice deployed — systematically avoided, used for methods conventions only, or used strategically to shift focus?
- Are sentences predominantly simple/compound, or does the writer build complex subordinated structures?
- What is the characteristic rhythm of sentence length — uniform, deliberately varied, or stochastically variable?
- Are em-dashes, colons, and semicolons used structurally (to signal logical relationships) or avoided?

**Failure mode:** Passive voice patterns in methods sections are a genre convention, not a voice marker. Ignore them unless the writer deviates from the convention distinctively — e.g., systematically using active voice in methods where peers would use passive.

---

## Dimension 2 — Semantic Writing Style

**What it captures:** How meaning is constructed and layered. How the writer handles abstraction, concreteness, analogy, and the movement between physical intuition and formal statement.

**What to look for:**
- Does the writer ground abstract claims in physical or mechanistic intuition before formalizing, or formalize first and interpret after?
- How are analogies deployed — sparingly as anchors, liberally as scaffolding, or avoided in favor of direct statement?
- Does the writer prefer concrete instantiation ("in the case where temperature exceeds 300K") or general statement ("under high-temperature conditions")?
- How densely are claims layered — does a single sentence carry one idea or multiple simultaneously?
- Is there a characteristic movement between scales (e.g., from mechanism to implication to broader significance)?

**Failure mode:** "Uses concrete examples" is nearly universal in good technical writing. The diagnostic signal is *when and how* the writer moves between abstraction levels, and whether the movement follows a consistent pattern.

---

## Dimension 3 — Vocabulary and Lexical Choices

**What it captures:** Characteristic word choices that persist across contexts — preferred technical terms, connective language, hedging vocabulary, and words the writer reaches for that peers might not.

**What to look for:**
- Are there preferred technical synonyms where multiple options exist? (e.g., "equilibrium" vs. "steady state," "constrain" vs. "bound")
- What is the characteristic hedging vocabulary? ("suggests," "indicates," "demonstrates," "implies," "is consistent with") — and where on that confidence spectrum does the writer typically sit?
- Are there signature connective phrases that recur? ("critically," "notably," "importantly," "in this context")
- Does the writer coin or appropriate terms in characteristic ways?
- What is the Latinate/Germanic ratio — does the writer prefer Latinate formal register or reach for shorter Anglo-Saxon words under pressure?

**Failure mode:** Domain-specific jargon is shared vocabulary, not personal vocabulary. Flag only words or phrases where alternatives exist and the writer has a consistent preference among them.

---

## Dimension 4 — Rhythm and Cadence

**What it captures:** The temporal and prosodic feel of the writing at sentence, paragraph, and section scales. How the writer controls pacing, builds toward emphasis, and uses structural variation for effect.

**What to look for:**
- **Sentence level:** Is there a characteristic short-long-short rhythm, or long sentences with periodic short punches? Where do short sentences appear — as topic sentences, as emphatic closers, as transitions?
- **Paragraph level:** How are paragraphs opened and closed? Does the writer use topic sentences consistently, or open in medias res? Do paragraphs end on the claim, on evidence, or on implication?
- **Section level:** Is there a characteristic build structure — broad framing → specific claim → evidence → interpretation → implication? Or does the writer invert this?
- How does the writer handle list structures — do they appear frequently, sparingly, or only for specific rhetorical purposes?

**Failure mode:** Paragraph length and list usage vary heavily by journal conventions and co-author influence. Weight patterns that persist across venues more heavily than those that appear in only one publication context.

---

## Dimension 5 — Epistemic Stance

**What it captures:** How the writer signals certainty, uncertainty, and the evidentiary basis of claims. This is one of the most individually distinctive dimensions and one of the hardest to imitate without explicit instruction.

**What to look for:**
- Where does the writer commit vs. hedge — is there a consistent threshold of evidence required before asserting rather than suggesting?
- How are counterarguments handled — preemptively acknowledged, incorporated, dismissed, or ignored?
- Does the writer distinguish between "our results show X" and "X is the case" — i.e., is the evidentiary source of claims consistently flagged?
- How is uncertainty quantified vs. qualitatively described?
- Is the writer's default stance confident-with-caveats or cautious-with-endorsements?

**Failure mode:** Epistemic conservatism in conclusions is a genre norm for peer-reviewed science. The diagnostic signal is deviation from the norm — either more assertive or more hedged than peers — and the specific vocabulary used to modulate certainty.

---

## Dimension 6 — Argumentation Structure

**What it captures:** The logical architecture of how cases are built. Not just what is argued but the sequence and dependency structure of the argument's components.

**What to look for:**
- Does the writer lead with the physical/mechanistic explanation and then present evidence, or present evidence and then interpret?
- How are multiple lines of evidence assembled — convergent (all pointing to same conclusion), sequential (each enabling the next), or parallel (independent support)?
- Where does the writer place the "so what" — early as a frame, late as a payoff, or distributed throughout?
- How are limitations handled — proactively, defensively, or minimized?
- Is there a characteristic way the writer handles the transition from results to interpretation?

**Failure mode:** Argument structure in papers is heavily constrained by IMRaD conventions. The signal is in proposals and review articles where structure is discretionary, and in the micro-structure within sections rather than the macro-structure across them.

---

## Dimension 7 — Transition Logic

**What it captures:** The connective tissue between ideas — how the writer moves from one sentence, paragraph, or section to the next. This is often the most fingerprint-like dimension because it is largely unconscious.

**What to look for:**
- What is the characteristic transition vocabulary at the sentence level? ("however," "therefore," "this implies," "critically," "building on this")
- Does the writer use backward-looking transitions (referencing what was just said) or forward-looking ones (signaling what comes next)?
- How explicit are logical connections — does the writer state the inferential step or leave it implicit for the reader?
- Are section transitions written as summaries, as pivots, or as direct bridges?
- Is there characteristic use of rhetorical questions as transitions?

**Failure mode:** Some transition words are universal scientific connectives with no diagnostic value ("however," "therefore" in isolation). The signal is in *combinations* and *placement* — e.g., always opening a paragraph with a backward-looking summary sentence before pivoting forward.

---

## Dimension 8 — Quantitative and Figure Integration

**What it captures:** How the writer narrates numbers, equations, and visual content. The relationship between quantitative content and the prose that surrounds it is highly individual.

**What to look for:**
- Do equations receive a motivating sentence before them, or are they dropped in and explained after?
- How are figures referenced — as primary evidence ("Figure 3 shows"), as illustration ("as illustrated in Figure 3"), or as supplementary confirmation ("consistent with Figure 3")?
- Does the writer re-interpret figure results in prose or simply direct the reader to them?
- How are numerical results reported — with explicit uncertainty, with comparative framing, with physical interpretation immediately attached?
- Is there characteristic use of order-of-magnitude reasoning or limiting-case analysis in the prose?

**Failure mode:** Figure citation style is often imposed by journal or co-author convention. Distinguish the writer's habitual pattern from venue-specific formatting requirements by looking for consistency across multiple publication venues.

---

## Dimension 9 — Register Modulation

**What it captures:** How the writer's voice *shifts* across different writing contexts — methods vs. significance sections in papers; specific aims vs. broader impact in proposals; formal review vs. collegial email. The modulation pattern itself is a voice characteristic.

**What to look for:**
- How much does sentence complexity change between high-stakes narrative sections (significance, introduction) and technical sections (methods, supplementary)?
- Does hedging language increase or decrease in proposal writing compared to papers?
- How does the writer handle the "sell" register of proposals — does it feel natural, strained, or does the writer find a characteristic way to make advocacy feel like analysis?
- In reviews and correspondence, what survives from the formal writing voice and what drops away?
- Is the writer's voice more or less distinctive (relative to peers) in one register than another?

**Failure mode:** Register differences that merely reflect genre conventions tell you nothing about the writer. The signal is in *how* the writer navigates required register shifts — whether they lean into them, resist them, or find hybrid solutions that are recognizably theirs.

---

## Notes on synthesis

After batch extraction, observations across dimensions should be cross-checked for:

- **Redundancy:** If two dimensions captured the same habit, consolidate into the stronger framing
- **Genericity:** Discard any observation that would apply to most competent writers in the field
- **Conflict:** If batches disagree on a dimension, note the conflict — it may reflect genuine register variation or corpus skew rather than an error. Check the document type classification of the conflicting batches before concluding there is a contradiction; apparent conflicts often resolve as register differences once type is accounted for
- **Corpus skew:** Check whether a strong observation is supported across multiple document types or appears only in one. An observation that appears only in proposals may be proposal-register behavior, not invariant voice. Flag it as type-specific rather than discarding it — type-specific patterns are still useful for the corresponding output context
- **Weight:** Not all dimensions will be equally diagnostic for all writers. A final SKILL.md should foreground the 3–4 dimensions with the strongest signal for this particular writer, not treat all nine as equal
- **Register modulation (Dimension 9):** Assess this dimension last, by comparing observations across document types. Describe how the writer's voice shifts across contexts, what invariants survive all registers, and which dimensions are most vs. least stable across the corpus

The goal of synthesis is a SKILL.md that a stranger could read and produce writing that a colleague of the author would recognize — not as imitation, but as sounding like it came from the same mind.
