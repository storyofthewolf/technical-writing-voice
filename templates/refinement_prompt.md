# refinement_prompt.md

You are refining an existing SKILL.md by incorporating observations from one or more
new batch notes. The current SKILL.md and new batch notes are provided above this
instruction block, along with corpus weight information.

---

## Your task

Compare the new batch notes against every dimension in the current SKILL.md.
For each dimension, determine which of three cases applies:

---

### Case 1 — Confirmation

The new document supports an existing pattern. The pattern is correct as written
or could be sharpened with new evidence.

**Action:** Update the pattern's wording if the new evidence is more precise or
more specific than the current wording. Update the corpus metadata block
(token count, document count, date). No other changes required.

Mark confirmed patterns with a brief inline note: `[confirmed: doc_id]`

---

### Case 2 — Addition

The new document reveals a pattern not currently in SKILL.md.

**Action:** Add the new observation to the appropriate dimension section.
Use the influence weight provided in the batch notes header to calibrate
how prominently to present the addition:

- Influence > 20%: add as a core pattern candidate, flag as single-document
- Influence 10-20%: add as a secondary pattern, flag as single-document
- Influence < 10%: add as a footnote observation, flag for confirmation
  by future documents before elevating

Tag all additions: `[new: doc_id, influence X%]`

---

### Case 3 — Contradiction

The new document's evidence conflicts with an existing SKILL.md pattern.

**Action:** STOP. Do not update SKILL.md. Instead, output a CONFLICT REVIEW block
(see format below) and nothing else after it.

A contradiction is genuine when:
- The new evidence directly contradicts the existing pattern in the same
  document type (e.g., new journal paper shows opposite syntax habit from
  existing journal paper observations)

A contradiction is NOT genuine (resolve silently) when:
- The conflict is between different document types — this is register variation,
  not contradiction. Note it as a type-specific delta in D9.
- The new document has influence < 5% and the existing pattern has strong
  multi-document support — flag in synthesis notes but do not stop.

**CONFLICT REVIEW block format:**

```
## CONFLICT REVIEW

**Dimension:** [D1-D9]
**Existing pattern:** [quote the current SKILL.md pattern verbatim]
**Conflicting evidence:** [quote the relevant observation from new batch notes]
**Document:** [doc_id], influence [X%]
**Existing support:** [how many documents / what token weight supports the current pattern]

**Possible explanations:**
1. The existing pattern is wrong or overstated — the new document corrects it
2. This is voice evolution — the writer's habits changed around [approximate period]
3. This is register variation — the conflict dissolves when document types are separated
4. The new document has co-author influence that suppresses this writer's natural pattern

**My assessment:** [which explanation is most likely and why]
**My recommendation:** [what you would do if you were allowed to proceed]

WAITING FOR YOUR INPUT. Do not update SKILL.md until you respond.
To proceed: edit this response file to remove the CONFLICT REVIEW block,
add a resolution note, and rerun: python refine.py --apply SKILL.md <response_file>
```

---

## Corpus metadata update

Always update the SKILL.md corpus metadata block to reflect the new totals:
- Increment document count
- Increment raw and effective token counts
- Update analysis date

---

## Output

If there are no conflicts: produce the complete updated SKILL.md as a downloadable
markdown artifact named `SKILL.md`. Not a diff, not a summary — the full document.

If there is a conflict: produce a downloadable markdown artifact named
`conflict_review.md` containing only the CONFLICT REVIEW block. Do not produce SKILL.md.

The SKILL.md should retain all existing content and structure. Only change what
the new evidence justifies. Conservative updates are correct. Aggressive rewrites
based on a single low-influence document are not.

The YAML front matter block at the very top of SKILL.md (between --- delimiters)
must be preserved exactly as-is on every refinement. Do not modify the name or
description fields unless the writer's name or field has changed.

The "Instructions for Claude" block must also be preserved exactly as-is on every
refinement. Do not modify, summarize, or move it. It is a behavioral directive,
not descriptive content.
