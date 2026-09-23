---
name: [skill-name-slug]
description: Applies [writer name]'s formal writing voice, learned from a
  corpus of journal papers and grant proposals in [field]. Use whenever
  drafting or revising prose on [writer name]'s behalf, including manuscripts
  in a LaTeX/Overleaf project (argument structure, figure narration, results
  phrasing) and professional emails, letters, statements, and other drafts.
  Governs prose voice and argument structure only; markup and citation
  mechanics follow standard conventions.
---

# SKILL.md — [writer name] Writing Voice

---

## Instructions for Claude

You are drafting and editing prose on behalf of [writer name]. Decide first which
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

**Name / handle:** [name]
**Field:** [primary discipline and subfield]
**Career stage:** [early / mid / senior]
**Corpus summary:** [e.g., "5 lead-author journal papers + 1 led proposal"]
**Analysis date:** [YYYY-MM]

## Corpus metadata
<!-- Updated automatically by skill.py on each run. Do not edit by hand. -->

**Documents processed:** [N]
**Raw prose tokens:** [N — informational corpus size; not a weight]
**Last updated:** [YYYY-MM-DD]
**Version:** [N]

**One-paragraph voice characterization:**
[4–6 sentence portrait. The dominant impression a colleague would have of this
writer's manuscript prose. Anchored in the 2–3 most distinctive patterns.]

---

## Dimensions
<!-- Ordered by signal strength, highest first. Only HIGH and strong MEDIUM
     dimensions get full sections. Weak dimensions go in "Lesser patterns" or
     are omitted. Keep within the token budget. -->

### Dimension [N] — [name]
**Priority:** [HIGH / MEDIUM]

**Core pattern:**
[2–4 sentences. Specific and falsifiable — something a stranger could apply
immediately. If it cannot be made specific, cut the dimension.]

**Secondary patterns:**
- [specific, falsifiable observation]
- [specific, falsifiable observation]

**Failure mode reminder:**
[One sentence on the false-positive risk for this dimension for this writer.]

---

### Dimension [N] — [name]
**Priority:** [HIGH / MEDIUM]

**Core pattern:**
[2–4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [name]
**Priority:** [HIGH / MEDIUM]

**Core pattern:**
[2–4 sentences]

**Secondary patterns:**
- [observation]

**Failure mode reminder:**
[one sentence]

---

## Lesser patterns
<!-- One short paragraph or a few bullets covering MEDIUM/LOW dimensions that
     are real but not strongly diagnostic. Keep brief. Omit entirely if there
     is nothing worth saying. -->
[brief notes, or omit]

---

## Manuscript-type notes
<!-- The single register delta worth recording: what shifts between a journal
     paper and a grant proposal. A few lines only. No other document types. -->

**Journal paper:** [what the voice does in paper body text]
**Proposal:** [the advocacy/feasibility register delta — gap-filling argument,
feasibility/cost arithmetic, "necessary and achievable" framing]

---

## Synthesis notes
<!-- Brief. Keeps the skill updatable when new documents are added. -->

**Corpus representativeness:** [how representative is this corpus]
**Cut during synthesis:** [what was dropped as generic or weak, and why]
**Paper/proposal divergence:** [any, and how resolved]
**Known gaps:** [what would strengthen the model if added later]
