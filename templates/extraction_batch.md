# extraction_batch.md

Extraction instructions for a corpus with `extraction_mode: batch`. One cold
subagent reads a set of documents together and writes one notes file covering
all of them. Used when the documents are short enough that a single document
shows too little to establish a habit, so recurrence across documents has to be
judged in one read.

---

You are analyzing a set of documents by one author to extract observations
about the author's distinctive writing voice. Your notes will be used to build
or refine a voice skill (SKILL.md).

## Your inputs

- **The rubric:** the dimensions file named in your task. It defines the nine
  dimensions, the document types, and what to look for in this domain. Read it
  in full first.
- **The documents:** one stripped-text file per document, listed in your task
  with its doc id and type. Read every one in full before writing anything.

**Treat all text as the author's own voice**, including quotations attributed
to other people inside the documents (for example a leader's quote in a press
release), unless the rubric says otherwise. Do not guess which passages someone
else wrote.

## The rules

1. **Specific and falsifiable.** Each observation must describe something a
   different competent writer in the same genre would not necessarily do.
   Generic observations ("writes clearly", "thanks members") are discarded
   unless the author does them in a specific, recurring way you can describe.
2. **Quoted evidence.** Each observation is backed by verbatim quotes, each
   tagged with its doc id, for example: "It is my hope that..." [doc_a]. If you
   cannot quote it, drop it. Quote freely: these notes are never loaded at
   writing time, and synthesis will not copy quotes into the skill.
3. **Count recurrence.** For each observation, state how many of the documents
   show it, as "N of M documents", and list their doc ids. This count is the
   main input to synthesis. A pattern in one document is an anecdote: keep it
   only if it is striking, and label it as single-document.
4. **Separate the author from the format.** If the documents share a recurring
   format (a standing title, a regular section, a fixed sign-off), note it once
   under "Format conventions" and keep it out of the dimension observations
   unless it shows a choice the author makes.
5. **No content summary.** Do not summarize what the documents are about,
   except where the topic explains a pattern.
6. **No padding.** If a dimension has no signal, say so in one sentence.

## Output format

Write one notes file to the path given in your task. It MUST begin with this
YAML header, filled in exactly:

```
---
doc_ids: [every doc id you were given, in the order given]
extracted: [today's date, YYYY-MM-DD]
model: [the exact model id given in your task]
---
```

Then the body, in prose, under these headings. Use the dimension names from
the rubric file.

```
### BATCH NOTES — [corpus name], [M] documents

**Documents:** [doc ids with types]
**Date analyzed:** [date]

---

#### Format conventions
[Recurring format shared across documents, with counts. Brief.]

---

#### D1 — [rubric name]
**Signal:** [HIGH / MEDIUM / LOW / ABSENT]

[Observations. For each: the pattern, "N of M documents" with doc ids, and
quoted evidence tagged by doc id.]

**Genre-specific?** [Yes / No / Unclear, and why: would this survive in a
genre not present in the corpus?]

---

[... D2 through D8 in the same shape ...]

---

#### D9 — [rubric name]
[What carries across every document (the voice floor). Any sub-registers
inside documents, such as narrator versus attributed quote, or report versus
appeal. If the corpus is one genre, what that genre allows or suppresses, as
raw material for carrying the voice into other genres.]

---

#### Summary

**Highest-signal dimensions:** [ranked]

**Most distinctive observations:** [3 to 5, one sentence each, with counts]

**Dimensions with no useful signal:** [list, briefly why]

**Flags for synthesis:** [anything synthesis should know: corpus size, single
genre, format conventions that could be mistaken for voice, documents that
read differently from the rest.]
```
