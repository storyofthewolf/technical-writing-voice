---
action: bootstrap
output_file: SKILL.md
generated: 2026-04-18 14:08
---

## Corpus metadata (for SKILL.md header)

- Documents processed: 3
- Raw prose tokens: 43,722
- Effective tokens (confidence-weighted): 26,233
- Analysis date: 2026-04


---

## Batch notes (all processed documents)


---
## Batch notes: wolf_2018

### BATCH NOTES — wolf_2018

**Document:** wolf_2018
**Type:** journal_paper
**Date analyzed:** 2026-04-18

---

#### D1 — Syntactic Style
**Signal:** HIGH

The author heavily relies on the imperative-adjacent phrase "Note that" to inject methodological caveats, definitions, or boundary conditions without disrupting the primary narrative flow. This appears frequently across different sections as a structural crutch for secondary exposition.
* "Note that ECS (units of K) is different from specific climate sensitivity..."
* "Note that for high-CO2 simulations, the total surface pressure grows significantly..."
* "Note that the temperatures shown in Figure 1c are an average..."

**Type-specific?** Unclear. This may be a general habit of the writer when explaining technical concepts, but it is highly visible here due to the density of methodological details required in a journal paper.

---

#### D2 — Semantic Style
**Signal:** MEDIUM

The author consistently uses the adjective "muted" to describe dampened or suppressed physical responses and system feedbacks, rather than standard alternatives like "reduced" or "dampened." 
* "the climate transition becomes muted"
* "larger values of $\alpha_{diff}$ imply a muted climate feedback"
* "subsequent modulations to clouds and the climate transition are muted"

**Type-specific?** No. This appears to be an ingrained semantic preference for describing dynamic systems.

---

#### D3 — Vocabulary
**Signal:** LOW

The vocabulary is almost entirely constrained by domain-specific climate modeling terminology (e.g., "equilibrium climate sensitivity," "q-flux," "pressure broadening continua"). There is one notable intrusion of slightly conversational, dramatic phrasing to describe data variance: "Estimates of deep-paleoclimate temperatures vary wildly, ranging possibly as high as ~340 K". 

**Type-specific?** Yes. Journal guidelines strictly bound lexical choices. 

---

#### D4 — Rhythm and Cadence
**Signal:** MEDIUM

Paragraphs are highly structured, often operating as self-contained logical units that follow a strict "Context -> Data/Action -> Synthesis" cadence. The synthesis sentence almost invariably begins with "Thus," bridging the granular model findings back to the macro-scientific implications.
* "Thus, it is reasonable to conclude that changes to atmospheric CO2 have acted as a significant driver..."
* "Thus, the sensitivity of climate accelerates under potential anthropogenic CO2 increases..."
* "Thus, warming the early Earth despite the faint young Sun may have benefited..."

**Type-specific?** Yes. This rigid paragraph architecture is heavily favored in peer-reviewed scientific literature to ensure clarity.

---

#### D5 — Epistemic Stance
**Signal:** HIGH

The author employs a highly defensive epistemic stance regarding methodology. They preemptively justify model simplifications by immediately citing their negligible impact on the macro-results, effectively closing off counter-arguments before they can be made.
* "Note that our control simulations, and also prior modeling work by others... suggest that removing permanent ice sheets has a relatively small overall impact on global mean climate."
* "While the CAM4 finite volume core is prone to spurious angular momentum errors; however, the inclusion of realistic topography minimizes these errors..."

**Type-specific?** Yes. This defensive framing is a direct product of the peer-review process.

---

#### D6 — Argumentation Structure
**Signal:** MEDIUM

The author explicitly bounds their claims and defines exactly what their metrics do *not* measure before discussing what they *do* measure. 
* "However, processes that operate on geologic time scales... are not considered in ECS. Thus ECS described in this work considers only so-called fast-feedbacks..."
* "All simulations are initiated from present-day global mean surface temperatures. We limit our study to climates warmer than ~280 K... Here our purpose is to study climate changes driven by CO2..."

**Type-specific?** Yes. Scope-bounding is a standard convention in scientific literature.

---

#### D7 — Transition Logic
**Signal:** HIGH

The author uses the temporal/spatial adverb "Here" or "Here we" as a primary transitional pivot to shift the focus from the literature review or general physical principles to their specific novel contributions and active methodology.
* "Here we use a 3-D climate system model to study..."
* "Here we evaluate our simulations following the commonly used methods..."
* "Here instantaneous forcings were calculated by outputting..."
* "Here we similarly find a transition to superrotation with warming climates..."

**Type-specific?** Unclear. It is highly prominent here, but whether it persists in less formal writing would require cross-document analysis.

---

#### D8 — Quantitative and Figure Integration
**Signal:** HIGH

The author actively instructs the reader on how to interpret the figures within the prose, often explicitly detailing the construction or the visual layout rather than relying solely on the caption. 
* "Plotted in this fashion, the adjusted radiative forcing and the transient evolution of the climate system are elucidated..."
* "Constructed in this fashion, Figure 5a illustrates the time-evolving behavior..."
* "In Figure 7 we have bracketed the temperature region associated with this climate transition with vertical dashed lines."

**Type-specific?** Yes. The reliance on figure integration is inherent to the data-heavy nature of the journal paper format.

---

#### D9 — Register Floor Observation

**Note:** The journal article format enforces a rigid, objective, and highly formalized register. It suppresses the author's personal voice, forcing reliance on structural signposting (e.g., "The remainder of the paper is organized as follows:") and passive/collective academic framing ("We find that..."). A more relaxed document type (like a blog post, email, or op-ed) would reveal whether the author uses more narrative transitions or maintains this strict structural rigidity.

---

#### Summary

**Highest-signal dimensions:** D1 (Syntactic Style), D7 (Transition Logic), D8 (Quantitative and Figure Integration).

**Most distinctive observations:**
* Uses "Note that..." repetitively as a syntactic device to inject parenthetical context or caveats without breaking sentence flow.
* Employs "Here" or "Here we" as a consistent transitional pivot to contrast general background with their specific methodological actions.
* Explicitly details the visual construction and intended reading method of data plots directly in the prose ("Constructed in this fashion...").

**Dimensions with no useful signal:** None. While D3 (Vocabulary) was constrained, it still provided a minor signal.

**Flags for synthesis:** This document was co-authored (Wolf, Haqq-Misra, Toon), meaning the observed style is likely a blended voice or heavily edited artifact. Observations should be cross-referenced against sole-authored documents (e.g., cover letters or personal projects) to isolate Wolf's distinct baseline style from his co-authors' influence and strict peer-review formatting.

---
## Batch notes: technical_emails

### BATCH NOTES — technical_emails

**Document:** technical_emails
**Type:** technical_email
**Date analyzed:** 2026-04-18

---

#### D1 — Syntactic Style
**Signal:** HIGH

Abruptly transitions between highly condensed, conversational fragments and dense, clause-heavy technical instruction. The author frequently employs instructional imperatives when discussing code, completely dropping narrative prose in favor of literal execution steps ("go to file calc_opd_mod.F90 , subroutine calc_gas_opd \n go to subroutine calc_gas_opd \n go to line 511"). 

**Type-specific?** Yes. The instructional imperative style is highly specific to debugging/mentoring emails and would not appear in formal publications.

---

#### D2 — Semantic Style
**Signal:** MEDIUM

The author frames technical problem-solving through a highly pragmatic, "triage" lens, relying heavily on colloquial metaphors to describe code interventions versus physical reality. The author contrasts "the nuclear option" with "a reasonable kludge" and refers to "tuning knobs" and "quick and dirty" solutions.

**Type-specific?** Yes. Informal metaphors for code manipulation ("kludgey", "nuclear option") are typical of correspondence but suppressed in formal papers.

---

#### D3 — Vocabulary
**Signal:** HIGH

The author natively intermixes atmospheric physics nomenclature (Rayleigh scattering, CIAs, asymmetry parameter), Fortran/CESM specific file/variable names (`cldfrc_rhminl`, `tau_gas(itc, ik)`, `pkg_cldoptics.F90`), and informal software engineering slang ("kludge", "refactor"). Variables and parameters are used directly as nouns in prose without translation ("setting w0 and G according to Mie or fractal aggregate").

**Type-specific?** Unclear. While the slang is email-specific, the willingness to write raw model variables directly into sentences rather than using their physical equivalents might persist in technical documentation.

---

#### D4 — Rhythm and Cadence
**Signal:** MEDIUM

Paragraphs predictably open with a terse, evaluative statement of 3-6 words before expanding into complex, multi-clause diagnostic reasoning. Examples: "This is a tricky one...", "Very interesting result.", "I am not quite sure what to suggest here.", "Cool!".

**Type-specific?** Yes. This conversational framing is highly specific to email dialogue.

---

#### D5 — Epistemic Stance
**Signal:** HIGH

The author exhibits a strictly empirical and cautious epistemic stance regarding model outputs, actively discouraging theoretical leaps when diagnostic tests are available. Uncertainty is managed by proposing specific sensitivity tests rather than speculation ("have you run sensitivity tests... to see how the solution evolves while changing this setting? At what point does spurious behavior start?"). The author treats the model as a chaotic system requiring isolation of variables ("The first thing I would check is ocean heat transport.")

**Type-specific?** No. This cautious, empirical approach to model validation is likely a core trait of the author's scientific worldview.

---

#### D6 — Argumentation Structure
**Signal:** HIGH

The author structures advice by explicitly stratifying solutions based on the recipient's career stage and publication timeline, prioritizing pragmatic output over ideal code health when necessary. Solutions are binned into "immediate purpose" ("quick and dirty solution... artificially limiting w0") versus "post-doc worthy" ("implementing the Heng improvements"). 

**Type-specific?** Yes. Mentorship and timeline-based technical triage are specific to interpersonal collaboration.

---

#### D7 — Transition Logic
**Signal:** LOW

Transitions are predominantly functional and list-like, addressing points linearly ("First...", "Another option...", "Other comments...").

**Type-specific?** Yes. Typical of email responses addressing multiple embedded questions.

---

#### D8 — Quantitative and Figure Integration
**Signal:** HIGH

The author embeds specific numerical boundaries, scaling factors, and code parameters directly into the flow of theoretical discussion, rarely separating the physics from the numerical limits ("limits are 10 bar and 500 K", "w0=0.99999...", "lowered cldfrc_rhminl from 0.9 to 0.88"). 

**Type-specific?** No. The tight coupling of physical theory and explicit numerical boundaries is likely present across all of the author's technical writing.

---

#### D9 — Register Floor Observation
**Note:** These emails reveal an author who treats climate models not just as mathematical representations, but as physical software artifacts with quirks, limitations, and "kludges." The email format allows the author to express skepticism about the models' default behaviors (e.g., the AM issue at >600K) and the realities of software maintenance (funding limitations for refactoring) that would be smoothed over or omitted in a peer-reviewed publication. It also reveals a willingness to mix highly technical troubleshooting with personal life updates (e.g., funding struggles, an aging dog).

---

#### Summary

**Highest-signal dimensions:** D1 (Syntactic Style), D6 (Argumentation Structure), D5 (Epistemic Stance).

**Most distinctive observations:** 1. The author explicitly tailors technical software solutions based on the recipient's career timeline (e.g., PhD urgency vs. Post-doc scope).
2. The author frequently drops prose entirely to issue raw, step-by-step code execution imperatives ("go to file...", "go to line...").
3. The author seamlessly uses raw Fortran variable names and namelist file paths as native nouns in physical theory discussions.

**Dimensions with no useful signal:** D7 (Transition Logic) — standard, functional email bulleting obscures any unique voice traits.

**Flags for synthesis:** Highly specific to mentorship/collaboration dynamics. The presence of exact code snippets and raw variable names is a strong identifier for this author's technical communication but may only be visible in correspondence or documentation, not formal papers.

---
## Batch notes: step2_proximab_final_scienceonly

### BATCH NOTES — step2_proximab_final_scienceonly

**Document:** step2_proximab_final_scienceonly
**Type:** proposal
**Date analyzed:** 2026-04-18

---

#### D1 — Syntactic Style
**Signal:** HIGH

The author frequently employs explicit ordinal sequencing within standard paragraph blocks to stack arguments or justifications, rather than breaking them into bulleted lists. For example: "First, the large-scale circulation... Second, only 3D models can provide... Third, 3D models can self-consistently simulate..." 

**Type-specific?** No. This paragraph-level stacking is likely a foundational habit of the writer's explanatory style, though the persuasive density is suited to a proposal.

---

#### D2 — Semantic Style
**Signal:** MEDIUM

The author intentionally weaves colloquial idioms into otherwise dense, highly technical physical descriptions to emphasize scale or importance. Examples include describing the star as "a cosmic stone’s throw away" and photochemical haze formation as a "double-edged sword." 

**Type-specific?** Yes. This slight informal intrusion is a common persuasive technique in grant proposals to maintain reviewer engagement and is likely suppressed in strict peer-reviewed journal articles.

---

#### D3 — Vocabulary
**Signal:** HIGH

The writer favors the prefix "astro-geophysical" (e.g., "astro-geophysical concerns," "astro-geophysical history") to bundle complex planetary evolution variables into a single conceptual noun. The term "unequivocally" is used as a hard amplifier for scientific targeting ("unequivocally the most promising target"). 

**Type-specific?** Unclear. "Astro-geophysical" is likely a permanent fixture of their vocabulary; the use of absolute amplifiers like "unequivocally" may be dialed up for proposal writing.

---

#### D4 — Rhythm and Cadence
**Signal:** MEDIUM

The text relies on a distinct rhythmic pattern: a long, heavily modified sentence outlining a complex physical mechanism, immediately followed by a short, declarative summary sentence that acts as a punchline. Example: "The incident stellar energy is shifted into the near-IR... Simultaneously, Rayleigh scattering becomes less important... [Long explanation]... Thus planets around M-dwarf stars are harder to freeze and easier to melt."

**Type-specific?** No. This "complex explanation followed by a blunt summary" is a fundamental pedagogic cadence.

---

#### D5 — Epistemic Stance
**Signal:** HIGH

The author bounds uncertainty by framing unknown historical states not as guesses, but as deterministic "evolutionary pathways" or "evolutionary outcomes." Even highly speculative scenarios are treated as concrete parameters to be constrained: "The migration scenario opens up many possibilities for Proxima b as it circumvents the super-luminous pre-main sequence phase." 

**Type-specific?** No. This reflects the writer's modeling-first mindset, where unknowns are just un-run parameter configurations.

---

#### D6 — Argumentation Structure
**Signal:** HIGH

The writer relies on a rigid "Acknowledge Precedent → Isolate Fatal Flaw → Insert Proposed Solution" argumentation loop. When discussing literature, they never merely cite; they systematically highlight the mechanical insufficiency of the cited work. Example: "Meadows et al. (2016) studied... but used 1D models that fundamentally cannot account for... Turbet et al. (2016) used a three-dimensional (3D) climate model, but only simulated a small subset..." 

**Type-specific?** Yes. This aggressive gap-identification is a hallmark of grant/proposal literature reviews.

---

#### D7 — Transition Logic
**Signal:** MEDIUM

Transitions between major sections rely heavily on referencing the previous section's specific deliverable or list as the input for the next section. Example: "We will compile a rich library of simulated 3D atmospheres... which we will then use to determine habitability..." and "See Section 1.2 for a full discussion... and see Section 1.3 for a discussion of each model".

**Type-specific?** Yes. High degree of internal cross-referencing is typical of dense, page-limited proposals.

---

#### D8 — Quantitative and Figure Integration
**Signal:** HIGH

Quantities are heavily integrated directly into the prose flow rather than isolated in tables, frequently using the tilde (~) to soften exactness in physical descriptions (e.g., "~12% as massive," "~65% of the present day solar flux," "~1.18 M⊕"). Note: Source text extraction contains OCR artifacts for Earth masses (`!⊕`), but the cadence of inline estimation is clear.

**Type-specific?** No. The habit of softening precise quantities with tildes in prose is likely a voice-invariant scientific habit.

---

#### D9 — Register Floor Observation
**Note:** The proposal format requires a highly persuasive, occasionally dramatized register ("humanity's first real chance," "unequivocally the most promising target") that reveals the author's willingness to use subjective, value-laden language when fighting for resources. A standard peer-reviewed paper would likely suppress this subjective urgency, forcing a colder register.

---

#### Summary

**Highest-signal dimensions:** Argumentation Structure (D6), Syntactic Style (D1), Epistemic Stance (D5).

**Most distinctive observations:** 1. Uses a "complex physical explanation followed by a blunt, idiomatic summary" sentence cadence (e.g., "harder to freeze and easier to melt").
2. Embeds explicit ordinal sequencing (First, Second, Third) within solid paragraph blocks rather than using lists.
3. Systematically frames prior literature by immediately highlighting mechanical or parameter limitations ("...but used 1D models that fundamentally cannot...").

**Dimensions with no useful signal:** None. The text provided rich signal across all queried dimensions.

**Flags for synthesis:** This is a grant proposal; expect the levels of assertive phrasing ("unequivocally") and colloquial idioms ("cosmic stone's throw") to be artificially elevated compared to the author's peer-reviewed publications. Any OCR artifacts (like `!⊕` for Earth masses) should be ignored as formatting errors, not stylistic choices.

---

## EVALUATION_DIMENSIONS.md (reference)

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


---

## SKILL_TEMPLATE.md (output format)

# SKILL.md — Technical Writing Voice

---

## Instructions for Claude

You are writing on behalf of [writer name]. Apply the voice model described in
this file to all writing tasks in this Project.

- **Match** the syntactic patterns, vocabulary preferences, epistemic stance,
  argumentation structure, and transition logic described in the dimensions below
- **Apply** the register-appropriate deltas from the per-context section based
  on the output type requested — a proposal section sounds different from an
  email, and both differ from a methods section
- **When uncertain** between two phrasings, prefer the one more consistent with
  the HIGH-priority dimensions described here
- **Do not default** to generic academic prose — the specific patterns in this
  file are the target, not a starting point
- **Preserve** this instruction block unchanged when updating SKILL.md

The one-paragraph voice characterization below is your primary orientation.
Read it first. The dimension sections provide the detail behind it.

---

## Writer identity

**Name / handle:** [name or anonymous]
**Field:** [primary discipline and subfield]
**Career stage:** [early / mid / senior — affects register expectations]
**Corpus summary:** [brief description — e.g., "14 first-author papers, 3 led proposals, 2 research statements, technical email corpus 2018–2024"]
**Analysis date:** [YYYY-MM]
**Corpus recency mode:** [uniform / recency — halflife N years]

## Corpus metadata
<!-- Updated automatically by refine.py on each refinement run. Do not edit by hand. -->

**Documents processed:** [N]
**Raw prose tokens:** [N]
**Effective tokens (confidence-weighted):** [N]
**Last updated:** [YYYY-MM-DD]
**Version:** [N — increments on each refinement run]

**One-paragraph voice characterization:**
<!-- 
    Write this last, after all dimensions are filled in. 
    It should read as a portrait of the writer — the kind of description
    a perceptive colleague would give. Aim for 4-6 sentences.
    This is what Claude reads first and uses to orient everything else.
-->
[A synthesized portrait of this writer's voice. What is the dominant impression?
What would a colleague recognize immediately? What is most distinctive about
how this person thinks on the page?]

---

## Dimensions
<!-- 
    Order these sections by signal strength — highest signal dimension first.
    A reader should be able to stop after the first 3 sections and still
    have a useful voice model.
-->

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence on why this dimension is ranked here — what makes it particularly distinctive or weak for this writer]

**Core pattern:**
[2-4 sentences describing the most distinctive, falsifiable observation for this dimension.
This is the signal — write it as something a stranger could apply immediately.
Avoid generic descriptions. If you cannot make it specific, the signal wasn't strong enough to include.]

**Secondary patterns:**
- [Additional observation — specific and falsifiable]
- [Additional observation — specific and falsifiable]
- [Add or remove bullets as needed]

**Type-specific notes:**
<!-- 
    Only include document types where this dimension behaves differently
    from the core pattern. Leave blank if the pattern is uniform across types.
-->
- *Journal paper:* [deviation from core pattern, or "consistent with core pattern"]
- *Proposal:* [deviation from core pattern, or omit if not applicable]
- *Technical email:* [deviation from core pattern, or omit if not applicable]

**Failure mode reminder:**
[One sentence on the specific false-positive risk for this dimension for this writer.
Copied or refined from EVALUATION_DIMENSIONS.md for the relevant dimension.]

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Type-specific notes:**
- *[Document type]:* [note]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Type-specific notes:**
- *[Document type]:* [note]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Type-specific notes:**
- *[Document type]:* [note]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension 9 — Register Modulation
**Priority:** [HIGH / MEDIUM / LOW]
<!-- 
    This dimension is always filled in last.
    It is assessed by comparing observations across document types,
    not from any single document. See EVALUATION_DIMENSIONS.md.
    The scaffold spectrum runs:
    Journal paper → Proposal → Review → Research statement → Letter of rec → Technical email
-->

**Invariant core:**
[What survives across all registers — the voice characteristics present whether
writing a methods section or a technical email. These are the deepest fingerprints.]

**Modulation pattern:**
[How does the voice shift as scaffold decreases? What is added, dropped,
or transformed as the writer moves from most to least constrained contexts?
2-4 sentences describing the overall pattern of change.]

---

## Register modulation — per-context deltas
<!--
    For each output context Claude might be asked to write in,
    describe what changes from the unified voice description above.
    These are deltas — only note what differs, not what stays the same.
    Omit contexts that are not relevant to this writer's use case.
-->

### Journal paper
**Tone shift:** [more/less formal, more/less hedged, more/less assertive than baseline]
**Structural conventions to observe:** [IMRaD section-specific notes — e.g., "active voice in discussion, passive in methods"]
**What to preserve from core voice:** [the 1-2 things that must survive even in the most constrained register]
**What to suppress:** [aspects of raw voice that don't fit this context]

### Proposal (grant narrative)
**Tone shift:** [how does advocacy register interact with this writer's default stance?]
**Structural conventions to observe:** [specific aims structure, significance framing, etc.]
**What to preserve from core voice:** [what makes this writer's proposals recognizable as theirs]
**What to suppress:** [what tends to undermine the advocacy register for this writer]

### Review article / perspective
**Tone shift:** [relative to baseline]
**What to preserve from core voice:** [key voice markers]
**What to suppress:** [what doesn't fit]

### Research statement
**Tone shift:** [relative to baseline]
**What to preserve from core voice:** [key voice markers]
**What to suppress:** [what doesn't fit]

### Peer review
**Tone shift:** [relative to baseline — collegial, critical, constructive?]
**What to preserve from core voice:** [key voice markers]
**What to suppress:** [what doesn't fit]

### Technical email / correspondence
**Tone shift:** [this is the low-scaffold floor — what is this writer like when unguarded?]
**What to preserve from core voice:** [what survives into informal register]
**What to suppress:** [what formal habits can be dropped]

---

## Synthesis notes
<!--
    Meta-observations from the synthesis process that don't fit cleanly
    into any single dimension but are useful for Claude to know.
    Examples: corpus skew that affects confidence, dimensions where
    conflicting signals were observed, notable voice evolution over time,
    dimensions that were discarded for genericity.
-->

**Corpus confidence:** [overall assessment — how representative is this corpus of the writer's current voice?]

**Discarded observations:** [dimensions or observations that were dropped during synthesis and why]

**Conflicting signals:** [any dimensions where document types disagreed, and how it was resolved]

**Voice evolution note:** [if temporal mode was set to recency, note what changed and when]

**Known gaps:** [document types absent from corpus that would strengthen the analysis if added later]


---

## Synthesis instructions

# synthesis_prompt.md

## How to use this prompt

This prompt is generated and pre-populated by `refine.py --bootstrap` and written
into `bootstrap_prompt.md`. You do not fill it in by hand.

**Workflow:**
1. Register and extract your bootstrap corpus documents using `corpus.py` and `extract.py`
2. Mark each document done with `extract.py --mark-done`
3. Run: `python refine.py --bootstrap > bootstrap_prompt.md`
4. Paste `bootstrap_prompt.md` into a Claude session
5. Save Claude's complete response as `SKILL.md` in your project directory
6. Run: `python refine.py --apply SKILL.md claude_response.md`

**To add documents later:** extract and mark them done, then run `refine.py` without
`--bootstrap`. It will generate a refinement prompt instead of a synthesis prompt.

---

## The prompt

Everything below this line is what `refine.py --bootstrap` embeds into
`bootstrap_prompt.md`, preceded by the batch notes and corpus metadata it generates.

---

You are synthesizing voice observations from batch extraction sessions into a completed
SKILL.md for a single writer. This SKILL.md will be loaded into a Claude Project as a
persistent Skill, enabling Claude to write in this writer's voice across all output
contexts — papers, proposals, reviews, emails, and other technical writing.

## Your inputs

The prompt above this instruction block contains:

- **Corpus metadata** — document count, raw token count, confidence-weighted effective
  token count. Use these to populate the SKILL.md corpus metadata block verbatim.
- **Batch notes** — one section per processed document, each containing voice
  observations across the nine evaluation dimensions. Each section includes the
  document type, confidence rating, prose token count, and any flags for synthesis.
- **SKILL_TEMPLATE.md** — the exact output format you must produce.
- **EVALUATION_DIMENSIONS.md** — definitions of all nine dimensions.

There is no weights.txt or corpus.yaml. Weighting information is embedded
directly in each batch notes section as document type, confidence, and token count.

## Your task

Produce a completed SKILL.md by working through the following steps in order.
Do not produce the SKILL.md until all steps are complete.

---

### Step 1 — Audit the batch notes

Read all batch notes and assess before doing anything else:

**Coverage:** Which document types are represented? Which are absent? Flag dimensions
where absent document types create meaningful gaps — for example, D8 (Quantitative
Integration) will be weak without journal papers or proposals; D6 (Argumentation
Structure) will be weak without proposals or research statements.

**Document count per type:** Single-document types have lower confidence than types
with multiple documents. Note which observations rest on a single document.

**Confidence distribution:** High-confidence documents (4-5) carry more signal than
low-confidence ones (1-2). If the batch is dominated by low-confidence documents,
note this as a corpus limitation.

**Flags from extraction:** Each batch notes section ends with a "Flags for synthesis"
entry. Collect all of these before proceeding — they are the extraction session's
warnings to you.

Produce a brief audit summary. You will include it in the SKILL.md synthesis notes
section. Do not proceed to Step 2 until the audit is complete.

---

### Step 2 — Resolve cross-document conflicts per dimension

For each of the nine dimensions, compare observations across all batch notes:

**Convergent observations** — patterns reported consistently across multiple documents
and document types. Weight these by: how many documents support them, the confidence
ratings of those documents, and their token counts. These are the strongest candidates
for SKILL.md core patterns.

**Divergent observations** — patterns that appear in some documents but not others,
or described differently across documents. For each divergence determine:
- Is this register variation by document type? (expected — note as type-specific delta)
- Is this temporal voice evolution? (note approximate period)
- Is this a single-document outlier at low confidence? (flag or discard)
- Is this a co-author influence artifact? (flag from extraction notes, then discard)

**Generic observations** — patterns flagged as discarded in batch notes. Cross-check:
if a pattern was discarded in one batch but reported as HIGH signal in another, do not
silently discard it. Flag the conflict in synthesis notes.

**Absent dimensions** — if a dimension returned ABSENT or only generic observations
across all documents, do not fabricate signal. Mark it LOW priority with an honest note.

Produce a per-dimension resolution log as internal working notes. Do not include it
in the SKILL.md, but use it to populate the dimensions accurately.

---

### Step 3 — Rank dimensions by signal strength

Using your resolution log, rank all nine dimensions from highest to lowest signal.

Signal strength is determined by:
- **Frequency** — how many documents reported this pattern
- **Consistency** — how similar were the descriptions across documents and types
- **Weight** — do high-confidence, high-token-count documents support this observation
- **Distinctiveness** — is the observation specific and falsifiable enough to distinguish
  this writer from peers in the same field

Assign each dimension a final priority: HIGH, MEDIUM, or LOW.
Aim for 2-4 HIGH, 3-4 MEDIUM, 1-2 LOW.

If fewer than 2 dimensions reach HIGH confidence, the corpus is insufficient for a
reliable voice model. Produce the SKILL.md anyway but open it with a prominent warning
block naming the specific document types that would strengthen it most.

---

### Step 4 — Synthesize D9 Register Modulation

D9 cannot be extracted from a single document type. Synthesize it here by comparing
the D9 register floor observations recorded across all batch notes.

Use the scaffold spectrum as your framework:

  Journal paper > Proposal > Review > Research statement > Letter of rec > Technical email
  most constrained                                                    least constrained

Identify:
- **Invariant core** — voice characteristics present across all document types, surviving
  even in the most constrained register. These are the deepest fingerprints.
- **Modulation pattern** — how voice shifts as scaffold decreases. What is added or
  amplified in low-constraint contexts? What is suppressed in high-constraint ones?
- **Per-context deltas** — for each document type present in the corpus, what
  specifically changes from the invariant core?

If only one document type is present in the corpus, mark D9 LOW priority and note that
it cannot be assessed until more document types are processed. Do not fabricate
cross-register observations from a single-type corpus.

---

### Step 5 — Write the one-paragraph voice characterization

Write this last, after all dimensions are resolved. It is the first thing Claude reads
when using the SKILL.md and must orient immediately.

Requirements:
- 4-6 sentences
- Reads as a portrait, not a checklist — do not enumerate dimensions
- Captures the dominant impression a perceptive colleague would have of this writer
- Anchors in the 2-3 most distinctive HIGH-priority observations
- Names the field and career stage so Claude knows the professional context
- Specific enough that it would not describe a different scientist in the same field

---

### Step 6 — Produce the completed SKILL.md

Using SKILL_TEMPLATE.md as your exact output format, produce the completed SKILL.md.

**Requirements:**

- Output the complete SKILL.md in full. Do not summarize, truncate, or say "fill in
  the rest." This document must be ready to save and use without any editing.
- Remove all HTML comment blocks from the template. The final SKILL.md
  contains no instructions, only content.
- Preserve the "Instructions for Claude" block at the top verbatim, substituting
  the writer's name for [writer name]. This block is a behavioral directive Claude
  reads at runtime — it must appear first, before the writer identity section.
- Order dimension sections by signal strength rank from Step 3, highest first.
  D9 Register Modulation is always last regardless of its priority rank.
- Every observation must be specific and falsifiable. If a dimension did not yield
  strong signal, say so honestly in one sentence rather than writing generic content.
- The register modulation per-context deltas section covers only document types
  present in the corpus. Omit types with no evidence.
- Populate the corpus metadata block from the metadata provided at the top of this
  prompt — document count, raw tokens, effective tokens, analysis date.
- Populate the synthesis notes section fully: corpus confidence assessment, discarded
  observations and why, conflicting signals and how resolved, voice evolution notes
  if temporal patterns were visible, known gaps from absent document types.
  This section is what makes the SKILL.md updatable when new documents are added later.

---

## Output

Produce the completed SKILL.md as a downloadable markdown artifact named `SKILL.md`.
Begin with the "Instructions for Claude" block. The artifact contains only the SKILL.md
content — no preamble, no commentary, nothing before or after the document itself.

