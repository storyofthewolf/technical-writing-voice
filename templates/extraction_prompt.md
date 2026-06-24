# extraction_prompt.md

You are analyzing a document to extract observations about the author's
distinctive technical writing voice. Your output will be used either to bootstrap
a SKILL.md (if this is an early document) or to refine an existing one (if
SKILL.md already exists).

**Treat all text in this document as the author's own first-author voice**,
regardless of any co-authorship. The corpus is curated at registration: a
document is only registered if its prose is representative of this author. Do not
attempt to guess which passages a co-author may have written — that judgment is
unfalsifiable from the text and produces noise. Read every sentence as the
author's.

The document text is embedded in the prompt above this instruction block.

---

## Your task

Analyze the document against the nine evaluation dimensions defined below.
Produce structured observations per dimension following the output format.

**The only rule that matters:** Every observation must be **specific and falsifiable**.
It must describe something that a different competent writer in the same field would
not necessarily do. Generic observations ("uses precise language," "structures
arguments logically") have zero diagnostic value and must be discarded.

**Every observation MUST be backed by a verbatim quote** from the document — the
exact words that exhibit the pattern, in quotation marks. If you cannot quote the
text that demonstrates a claim, you do not have evidence for it: drop the claim.
The quotes are the falsifiability check; they let a reader verify each observation
against the source. (They live only in these notes — synthesis distills them into
described patterns and does not copy them into the skill, so quote freely here.)

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

Produce one notes file named as specified in the `output_file` field of the
prompt front matter (e.g. `notes_DOCID.md`). In Claude Code, write it directly to
`batch_notes/notes_DOCID.md`; in a claude.ai session, return it as a downloadable
markdown artifact with that name.

The file MUST begin with a YAML front-matter header recording how the extraction
was made — this is the provenance the pipeline reads back to populate corpus
status. Fill it in exactly:

```
---
doc_id: [the document id]
extracted: [today's date, YYYY-MM-DD]
model: [the exact model id you are running as, e.g. claude-opus-4-8]
---
```

The `model` value must be your own exact model id, not a guess or a family name.
After the header, the body is prose — no other YAML, no structured schemas. Be
direct and specific. Use brief quotes from the text as evidence, to anchor
observations in actual language rather than impression.

---

### BATCH NOTES — [document id]

**Document:** [id]
**Type:** [type]
**Date analyzed:** [today's date]

---

#### D1 — Syntactic Style
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Your observations. Each one specific and falsifiable, and each anchored by a
verbatim quote from the document. If absent, say so in one sentence. No padding.]

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
unusual register for the document type, limited signal due to document length,
anything that affects how these notes should be read. Do NOT flag suspected
co-author influence: all registered text is treated as the author's own voice.]
