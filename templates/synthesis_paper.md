# synthesis_paper.md

Synthesis instructions for the **paper** profile. `skill.py --profile paper
--bootstrap` embeds everything below the line into the bootstrap prompt,
preceded by the batch notes (journal papers and proposals only) and the corpus
metadata it generates. You do not fill this in by hand.

This template differs from the general `synthesis_prompt.md` in three ways:

1. **Single register.** The corpus is manuscript-register only (journal papers
   and proposals). Do not assess cross-document-type register modulation (the
   old D9) — there is one target register, the formal manuscript.
2. **Slim output.** There is a hard length budget. Cut anything that is not a
   specific, falsifiable, applicable instruction.
3. **LaTeX is deferred.** This skill is loaded by Claude Code editing an
   Overleaf/LaTeX repo, but it governs prose voice and argument structure only.
   It must not prescribe LaTeX or .bib syntax — Claude uses its own best
   practices for those.

---

You are synthesizing voice observations from batch extraction sessions into a
slim, purpose-specific SKILL.md for **one writer writing formal scientific
manuscripts** — journal papers and grant proposals. The finished SKILL.md is
loaded by **Claude Code as a skill while the author edits a GitHub-backed
Overleaf project** (LaTeX source, .bib files, figures). Claude applies it
whenever drafting or editing manuscript prose or structuring the argument.

## Your inputs

The prompt above this instruction block contains:

- **Profile directives** — the skill name, the writing purpose, the token
  budget, and the LaTeX policy. Honor them exactly.
- **Corpus metadata** — document count and raw token count (informational corpus
  size; not a weight). Populate the SKILL.md metadata block from these.
- **Batch notes** — one section per processed document, restricted to journal
  papers and proposals. Each records voice observations across the evaluation
  dimensions plus a "Flags for synthesis" entry.
- **SKILL_TEMPLATE_PAPER.md** — the exact (slim) output format to produce.
- **EVALUATION_DIMENSIONS.md** — definitions of the dimensions, for reference.

## Scope discipline — read before you start

This is a **manuscript-voice** skill, not a general writing model. Hold to
these boundaries:

- **Prose voice and argument structure only.** Syntax, semantics, vocabulary,
  epistemic stance, argumentation, transitions, and quantitative/figure
  narration as they appear in the *body text* of papers and proposals.
- **Do NOT write LaTeX, .bib, or figure-markup conventions.** No guidance on
  `\citep` vs `\citet`, math environments, sectioning macros, caption syntax,
  or bibliography style. The author is deliberately deferring all markup
  mechanics to your standard best practices. Spending the budget on markup
  rules is explicitly unwanted. If a voice observation is really about markup
  (e.g. "uses `\sim`"), translate it to its prose intent ("approximations are
  marked with ~ and used with genuine precision-calibration") or drop it.
- **No informal-register material.** Emails, letters, and statements are out of
  corpus by design. Do not infer a casual register or describe "what the writer
  is like when unguarded." The target is the formal manuscript voice.

## Your task

Work through these steps in order. Do not emit the SKILL.md until all are done.

### Step 1 — Audit the batch notes

Read every notes section. Note which dimensions are reported HIGH consistently
across documents, which are weak, and collect every "Flags for synthesis"
entry (co-author contamination warnings especially — down-weight sections
flagged as co-author-influenced). Produce a short internal audit; you will
compress it into the synthesis-notes block at the end.

### Step 2 — Resolve observations per dimension

For each dimension, compare across documents:

- **Convergent** patterns reported across multiple papers/proposals are the
  core of the skill. All documents contribute evenly — judge strength by how many
  documents support a pattern and how consistently it is described, never by token
  count or any rating.
- **Divergent** patterns: decide whether the difference is paper-vs-proposal
  variation (note it as a brief delta) or a single-document outlier (drop it).
  There is no cross-register axis to appeal to here — both types are formal
  manuscripts, so genuine contradictions are rare and should be resolved toward
  the pattern with broader multi-document support.
- **Generic** observations (conventional for the field, not distinguishing this
  writer) are cut. Slimness depends on this.

### Step 3 — Rank dimensions and cut hard

Rank the dimensions by signal strength (frequency × consistency × weight ×
distinctiveness). Assign HIGH / MEDIUM / LOW.

For a slim skill, **only HIGH and the strongest MEDIUM dimensions earn full
sections.** Roll weak dimensions into a single short "Lesser patterns" note or
omit them. Do not pad a LOW dimension with generic prose to fill the template —
say it is not diagnostic in one clause and move on. A reader who stops after
the top three dimensions should already have a usable voice model.

### Step 4 — Note the paper vs. proposal delta (brief)

There is no cross-document-type register section. But journal papers and
proposals do differ in one respect worth a few lines: proposals carry an
advocacy/feasibility register (gap-filling argument, computational-cost
arithmetic, "this work is necessary and achievable") that papers do not. Record
this as a short **Manuscript-type notes** block — what shifts when the target is
a proposal section versus a paper section — and nothing more. Keep it to a
handful of lines.

### Step 5 — Write the one-paragraph voice characterization

Write this last. 4–6 sentences, a portrait not a checklist, anchored in the
2–3 most distinctive HIGH observations, naming the field and career stage. It
is the first thing Claude reads; it must orient immediately and be specific
enough that it would not describe a different planetary scientist.

### Step 6 — Produce the completed SKILL.md

Using SKILL_TEMPLATE_PAPER.md as the exact format:

- Output the complete SKILL.md in full — ready to save, no "fill in the rest."
- Remove all HTML comment blocks. The final file contains only content.
- Fill the YAML front matter:
  - `name`: the profile's `skill_name` (given in the profile directives above).
  - `description`: describe a Claude Code skill that applies this writer's
    formal manuscript voice when editing LaTeX/Overleaf paper and proposal
    files. State that it governs prose voice and argument structure, and that
    LaTeX/.bib/figure markup follows Claude's standard conventions.
  - Do not alter the rest of the front matter.
- Preserve the "Instructions for Claude" block verbatim, substituting the
  writer's name. It must appear immediately after the front matter. It already
  contains the LaTeX-defer clause — keep it.
- Order dimension sections by signal-strength rank, highest first.
- Every retained observation must be specific and falsifiable. If you cannot
  make it specific, cut it.
- **Honor the token budget** stated in the profile directives. If you are over,
  cut MEDIUM/LOW content and tighten prose — do not cut HIGH observations.
- Populate the corpus metadata block from the metadata at the top of the
  prompt.
- Fill the synthesis-notes block briefly: corpus representativeness, what was cut and
  why, any paper/proposal divergence, known gaps.

## Output

Produce the completed SKILL.md as a downloadable markdown artifact named
`SKILL.md`. Begin with the "Instructions for Claude" block. The artifact
contains only the SKILL.md content — no preamble, no commentary.
