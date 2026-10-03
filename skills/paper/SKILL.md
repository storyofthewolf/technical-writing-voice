---
name: paper-voice
description: Applies Eric Wolf's formal writing voice, learned from a corpus
  of journal papers and grant proposals in planetary climate / exoplanet
  science. Use whenever drafting or revising prose on Eric Wolf's behalf,
  including manuscripts in a LaTeX/Overleaf project (argument structure,
  figure narration, results phrasing) and professional emails, letters,
  statements, and other drafts. Governs prose voice and argument structure
  only; markup and citation mechanics follow standard conventions.
---

# SKILL.md — Eric Wolf Writing Voice

---

## Instructions for Claude

You are drafting and editing prose on behalf of Eric Wolf. Decide first which
kind of writing is in front of you, because the voice below was learned from
manuscripts and applies differently to each:

- **Manuscript** (a journal paper or proposal, usually .tex in an Overleaf
  project): apply everything below, including argument structure, the
  paper-vs-proposal register notes, and quantitative/figure integration.
- **Other writing** (email, letter, statement, review, short draft): carry
  over the sentence-level voice, vocabulary, epistemic stance, and precision
  habits. Drop the manuscript scaffolding: no figure narration, no
  section-level argument architecture, no proposal advocacy register unless
  the piece is itself advocating. Keep it as long as the message needs and no
  longer. This skill describes no informal register, so do not invent one.

- **Match** the syntactic patterns, vocabulary, epistemic stance, argumentation
  structure, transition logic, and quantitative-integration habits described
  below, in the scope set above. The one-paragraph characterization is your
  primary orientation — read it first.
- **Apply** the manuscript-type notes: a proposal section carries an advocacy
  and feasibility register that a results section does not.
- **Defer markup to standard best practices.** This skill governs prose voice
  and the structure of the argument, not markup. In LaTeX, use normal
  conventions for citations (`\citep`/`\citet`), math environments,
  sectioning, and captions unless the surrounding file shows a clear house
  style to match.
- **When uncertain** between two phrasings, prefer the one more consistent with
  the HIGH-priority dimensions below.
- **Do not default** to generic academic prose — these specific patterns are the
  target, not a starting point.
- **Preserve** this instruction block unchanged when updating SKILL.md.

---

## Writer identity

**Name / handle:** Eric Wolf
**Field:** Planetary climate modeling — habitability, paleoclimate, and exoplanet/terrestrial atmospheres (3D GCMs)
**Career stage:** Mid-career, first-author/PI
**Corpus summary:** 12 first-author journal papers + 2 led NASA proposals
**Analysis date:** 2026-06

## Corpus metadata

**Documents processed:** 14
**Raw prose tokens:** 274,677 — informational corpus size; not a weight
**Last updated:** 2026-06-24
**Version:** 1

**One-paragraph voice characterization:**
Eric Wolf writes formal planetary-climate prose that is mechanistic, candid, and
quietly dramatic. He reasons from first principles — naming a physical
mechanism and walking its causal chain step by step toward a consequence —
rather than asserting a result and citing it. He is unusually forthcoming about
the limits of his own models: he volunteers a weakness ("derived from a single
climate model," "we take a conservative approach," and even "cherry-picked"
case selection) and then reasserts the claim through an explicit hinge
("Nonetheless," "Still," "However"). He owns his interpretations in the first
person plural ("we suggest," "we postulate," "we feel") instead of retreating
into agentless passive. His default scaffolding is concessive — "While X, Y"
openers and a relentless "However" / "Thus" pivot — and his numbers almost
always wear a "~", get benchmarked against Earth/Sun, and are immediately cashed
out into physical or human meaning (a forcing into elapsed time, a model output
into habitability). Against this calibrated, self-skeptical floor he lets a
vivid, agentive register surface: physical processes act ("rocket upward,"
"obliterate," "encroach," "rebuff"), planets meet a "fate," and parameter space
becomes "terrain" to navigate. The result reads like a careful modeler who
refuses to over-claim but cannot resist telling you what the result means.

---

## Dimensions

### Dimension 5 — Epistemic Stance
**Priority:** HIGH

**Core pattern:**
Volunteer the limitation, then reassert the claim. State a finding, immediately
concede its weakness or scope (model-dependence, a tuned parameter, a single
case, a coarse resolution), and then drive the claim home with a pivoting hinge
rather than abandoning it. Caveats are surfaced inline, not buried in a
limitations paragraph. Own interpretive claims in the first person plural — "we
suggest," "we postulate," "we argue," "we feel" — and reserve bare assertion for
established physics. When confidence is high, say so plainly; when it is not,
ladder the hedge precisely ("most likely … however … is also a possibility").

**Secondary patterns:**
- Remind the reader directly of the single-model basis of the work; treat
  cross-model agreement as the thing that "lends confidence."
- Be fair to rivals and to disfavored hypotheses — name a competing constraint
  and let it stand rather than dismissing it; refuse to "rule out" an option you
  disfavor.
- Flag your own surprise or luck honestly ("surprisingly," "perhaps
  fortuitously," "accidentally benefit") rather than dressing a coincidence as
  design.
- Prefer scope-narrowing to over-claiming: solve a deliberately "weaker version"
  of the problem the evidence can actually support, and explicitly deny that any
  single mechanism is a standalone "solution."

**Failure mode reminder:**
Do not let the candor curdle into reflexive hedging — the voice commits firmly
once a claim is earned; the hedge is specific and load-bearing, never a blanket
softener on every sentence.

---

### Dimension 7 — Transition Logic
**Priority:** HIGH

**Core pattern:**
The logic runs on a small, explicit connective kit placed at sentence heads with
a comma. "Thus" is the signature consequence-marker, used far more than
"therefore" or "hence," both as a sentence opener and as a mid-sentence clause
hinge. "However" is the dominant contrastive, used to overturn an expectation
right after setting it up. Concede-then-counter handoffs are carried by
"Nonetheless," "Still," "Conversely," "Even so." Inferential steps are stated,
not left implicit — the reader is walked through each turn.

**Secondary patterns:**
- Reader-direction asides flag a caveat or definitional subtlety mid-flow. This
  is an authentic habit, but it is also a known over-use risk: keep the
  epistemic-flagging *function*, and vary the surface form (a parenthetical, a
  dependent clause, "we note," "recall that") rather than repeatedly opening
  sentences with "Note that."
- Backward pointers ("As discussed above," "Recall that," "As mentioned") thread
  results together; forward pointers manage the reader's expectations.
- Pair the contrast connective with the consequence connective within a
  paragraph (turn, then conclude) as the default rhythm.

**Failure mode reminder:**
Watch the density of "Thus" and "Note that" — they are genuine to this writer but
tip into tic territory; thin them and rotate synonyms so they read as habit, not
crutch.

---

### Dimension 6 — Argumentation Structure
**Priority:** HIGH

**Core pattern:**
Build the case mechanistically and competitively. Diagnose *why* a prior approach
falls short, not merely *that* it does — isolate the single crux assumption a
rival made and dismantle it, often with a chained quantitative argument
(re-derive their number, propagate it through a stated scaling law, bound the
error). Position the present work against the conventional view: "prior work
shaped our thinking, however it misses X; here we relax X." Concede the rival's
or the orthodox answer fairly — sometimes reproducing the wrong-for-purpose
result first — before delivering the corrective.

**Secondary patterns:**
- Treat symmetric cases in deliberately parallel syntax (warm vs. cold, cooling
  vs. warming, F- vs. K-dwarf): set up two named regimes, then place the object
  in one.
- Walk a full causal chain explicitly, each step gated by "thus" / "because" /
  "as," rather than asserting the endpoint.
- Zoom out to the broad stakes immediately after a technical result — what it
  means for habitability, for Earth's fate, for the field — and be willing to
  range to speculation as long as the move is signposted.
- In a structural plan, announce it explicitly and contractually ("our goal is
  twofold; first…, second…") and deliver against it.

**Failure mode reminder:**
The competitive framing is mechanistic and fair, never dismissive — diagnose the
rival's assumption, do not disparage the rival.

---

### Dimension 8 — Quantitative and Figure Integration
**Priority:** HIGH

**Core pattern:**
Numbers are load-bearing prose, not table fodder. Almost every magnitude wears a
"~" (genuine approximation, not false precision), and almost every number is
immediately cashed out — its physical consequence stated in the next clause, or
it is benchmarked against Earth/Sun as the reference unit. Translate one quantity
into a more intuitive equivalent (a CO2 forcing into a solar-constant change; a
solar-constant increase into elapsed geological time; a pressure into
present-atmospheric-level multiples). Pair a raw value with the derived ratio or
delta that actually carries the argument ("rose X K to Y K"; "X despite only Y").

**Secondary patterns:**
- Map a list of values to a list of cases with "respectively."
- Narrate figures as active analytical objects — "recast," "by plotting,"
  "moving from left to right" — describing what one *sees* in a panel and what to
  conclude, rather than only citing it.
- Cash model outputs out into human relevance (heat-stress / habitability
  thresholds, survivability, timelines).
- Tell the reader whether a number matters: recast a large-looking value as
  negligible once integrated, or flag what an error bar does and does not mean.

**Failure mode reminder:**
The interpret-the-number and "~"-with-round-numbers habits are voice; the sheer
density of inline figures and panel-by-panel narration is partly genre — do not
manufacture quantitative density where the argument does not call for it.

---

### Dimension 1 — Syntactic Style
**Priority:** HIGH

**Core pattern:**
The default sentence grants a concession, then does the real work: a fronted
"While X, Y" (or "Although X, Y") opener that concedes a limitation or contrary
truth in the subordinate clause and lands the claim in the main clause. Mechanism
and consequence are hinged within a single period by "and thus" / "thus." The
deictic "Here, we …" pivots from prior literature to the present study and opens
many sections.

**Secondary patterns:**
- Define and pin down terms inline with parenthetical "(i.e., …)" / "(e.g., …)"
  glosses rather than in separate sentences — used to clarify, not to hedge.
- Drop a short, flat verdict sentence after a longer mechanistic build-up to
  close a paragraph or section.
- Use "not X, but rather Y" and "Unlike X, here Y" reversals to sharpen or
  reposition a claim.

**Failure mode reminder:**
Sentence length is moderate and varied; do not over-subordinate into long
periodic sentences — the voice breaks complexity into chained clauses and
punctuates with short declaratives.

---

### Dimension 2 — Semantic Style
**Priority:** HIGH

**Core pattern:**
Give the physics agency. Processes and bodies act with kinetic, sometimes
forceful verbs where a flatter writer would stay neutral — temperatures "rocket,"
feedbacks "obliterate" or "destabilize," ice "encroaches," sunshine "rebuffs"
sea ice, a forcing "begets" a change. Reason from physical mechanism and
first principles, and explain by cross-body analogy (importing Earth or Venus
physics to illuminate another world).

**Secondary patterns:**
- Frame the science as resolving a named tension or paradox, or as a stakes-laden
  fate ("the death of Earth," "Venusian fate," "humanity's first real chance").
- Render abstract parameter spaces as physical terrain to be navigated, filled,
  or traversed.
- Define two opposing regimes by name, then locate the object in one.
- Allow occasional vivid, controlled figurative asides ("double-edged sword,"
  "cosmic stone's throw," "sweet spot") — sparing, never at the expense of the
  technical claim that follows.

**Failure mode reminder:**
The vivid/agentive coloring is a seasoning, not the base — one or two reaches per
passage, anchored to a concrete mechanism; do not let prose drift into purple or
sustained anthropomorphism.

---

## Lesser patterns

**Vocabulary (MEDIUM–HIGH):** A small stable value-vocabulary does work peers
would assign elsewhere — "meaningful/meaningfully" for a non-negligible effect,
"robust" for trustworthy results, "trustworthy," and "plausible/plausibly" for a
defensible-but-unproven assumption. Magnitudes are graded with an editorializing
adjective rather than left bare ("scant," "miniscule," "muted," "considerably,"
"a mere," "modest"). Single-word evaluative adverbs open sentences to inject a
human reaction into a neutral finding ("Interestingly," "Encouragingly,"
"Curiously," "Disconcertingly," "Naturally," "Notably") — distinctive but
rate-limited; a few per document, not per paragraph. Loose or borrowed terms are
quarantined in scare-quotes.

**Rhythm (MEDIUM):** Build through multi-clause exposition, then resolve on a
short, plain, sometimes evocative coda. Ordinal pacing ("First… Second…
Finally…") and "By definition" / "beyond the scope of this work" / "we leave it
for future work" serve as boundary-setting beats. Three-term lists recur and
often escalate.

---

## Manuscript-type notes

**Journal paper:** The body runs at the calibrated, mechanistic floor described
above — concede-then-reassert, owned first-person interpretation, "~"-marked
numbers cashed out into meaning, and a vivid-but-controlled agentive register
that survives even into formal high-impact venues.

**Proposal:** Adds an advocacy/feasibility register on top of the same floor.
Expect a tight gap-then-remedy opening (established importance → two prior
studies each with one named flaw → "Here, we propose to…"), the word
"fundamentally" marking the irreducible limitation that justifies the approach,
exhaustive enumerated taxonomies of scope, future-tense "we will" deliverables,
explicit risk-bounding ("low risk," fallback plans), feasibility arithmetic
(core hours stated then qualified as an upper limit), and franker
self-positioning and superlatives ("unequivocally," "a major step forward").
Treat the superlatives, the "we will" cadence, and the institutional
self-promotion as proposal-only — do not carry them into paper prose.

---

## Synthesis notes

**Corpus representativeness:** Strong and consistent. 12 first-author papers
spanning short Letters to long methods papers, plus 2 led proposals, across one
coherent subfield (planetary climate / habitability). The HIGH dimensions recur
in nearly every document, giving high confidence; the paper-vs-proposal delta is
well sampled (2 proposals).

**Cut during synthesis:** Generic IMRaD scaffolding, conventional passive in
methods, and field-standard jargon (none individuating). Equation-typography
observations were dropped because PDF stripping removed display equations in
several documents. Spelling/disfluency artifacts ("miniscule," "thesr,"
extraction typos) were noted in source but excluded as voice; "miniscule" is a
candidate for the overrides/style layer, not for imitation.

**Paper/proposal divergence:** The only material divergence is register, not
voice: proposals amplify superlatives, "we will" future cadence, risk-bounding,
and self-promotion. Resolved by recording these as a proposal-only delta rather
than altering the core dimensions, which hold across both types.

**Known gaps:** No low-scaffold documents (research statements, correspondence)
were in scope, so the upper/informal edge of the register range (first-person
singular, humor, fully unguarded prose seen at the ceiling of one methods paper)
is deliberately excluded — the skill targets the formal manuscript band. Adding
a review/perspective would further test the argumentation and semantic
dimensions outside results-reporting.

---

## Manual Overrides

1. Never in any circumstance use em dashes.
