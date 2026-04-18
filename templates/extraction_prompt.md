# extraction_prompt.md

You are analyzing a document written by a single author to extract observations
about their distinctive technical writing voice. Your output will be used either
to bootstrap a SKILL.md (if this is an early document) or to refine an existing
one (if SKILL.md already exists).

The document text is embedded in the prompt above this instruction block.

---

## Your task

Analyze the document against the nine evaluation dimensions defined below.
Produce structured observations per dimension following the output format.

**The only rule that matters:** Every observation must be **specific and falsifiable**.
It must describe something that a different competent writer in the same field would
not necessarily do. Generic observations ("uses precise language," "structures
arguments logically") have zero diagnostic value and must be discarded.

**What you are NOT doing:**
- Describing whether this is good writing
- Summarizing the document's scientific content
- Noting genre conventions that all writers in this field follow
- Inventing observations to fill space if a dimension has no signal

**On figures and tables:** You have text only. Do not speculate about figures.
Figure captions that survived text extraction are valid evidence; treat them as prose.

**On document type:** The document type is noted in the prompt header. Note which
observations may be type-specific (only visible in this genre) vs. likely
voice-invariant (would appear across all this writer's output).

---

## Output format

Produce your output as a downloadable markdown artifact named as specified in the
`output_file` field of the prompt front matter (e.g. `notes_DOCID.md`).
No YAML, no structured schemas. Be direct and specific. Use quotes from the text
as evidence — brief ones, to anchor observations in actual language rather than impression.

---

### BATCH NOTES — [document id]

**Document:** [id]
**Type:** [type]
**Date analyzed:** [today's date]

---

#### D1 — Syntactic Style
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Your observations. Each one specific and falsifiable, with a brief textual example.
If absent, say so in one sentence. No padding.]

**Type-specific?** [Yes/No/Unclear — and why]

---

#### D2 — Semantic Style
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note.]

**Type-specific?** [Yes/No/Unclear]

---

#### D3 — Vocabulary
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note.]

**Type-specific?** [Yes/No/Unclear]

---

#### D4 — Rhythm and Cadence
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note.]

**Type-specific?** [Yes/No/Unclear]

---

#### D5 — Epistemic Stance
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note.]

**Type-specific?** [Yes/No/Unclear]

---

#### D6 — Argumentation Structure
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note.]

**Type-specific?** [Yes/No/Unclear]

---

#### D7 — Transition Logic
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note.]

**Type-specific?** [Yes/No/Unclear]

---

#### D8 — Quantitative and Figure Integration
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations or absent note. If text-only extraction removed equations, note that.]

**Type-specific?** [Yes/No/Unclear]

---

#### D9 — Register Floor Observation
**Note:** D9 (Register Modulation) is assessed during synthesis across document types,
not from a single document. Instead, record:

What does this document type allow or reveal about this writer's voice that a more
constrained document type might suppress? This is the raw material for D9 at synthesis.

[Your observation.]

---

#### Summary

**Highest-signal dimensions:** [list by signal strength]

**Most distinctive observations:** [2-3 observations most likely to distinguish
this writer from peers in the same field. One sentence each.]

**Dimensions with no useful signal:** [list and briefly why]

**Flags for synthesis:** [anything the synthesis or refinement session should know —
suspected co-author influence, unusual register for the document type, low confidence
due to document length, anything that affects how much weight to put on these notes]
