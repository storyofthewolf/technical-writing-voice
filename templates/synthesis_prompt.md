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
- The file begins with a YAML front matter block (between --- delimiters). Fill in:
  - `name`: a lowercase hyphenated slug from the writer's name (e.g. `eric-wolf-voice`)
  - `description`: replace [writer name] and [field] with the actual name and field
  - Do not alter any other part of the front matter block
- Preserve the "Instructions for Claude" block verbatim, substituting the writer's
  name for [writer name]. This block is a behavioral directive Claude reads at runtime
  — it must appear immediately after the front matter, before the writer identity section.
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
