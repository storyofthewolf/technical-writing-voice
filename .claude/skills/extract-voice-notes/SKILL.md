---
name: extract-voice-notes
description: Run voice extraction for one corpus inside Claude Code. Strips
  pending documents (.pdf, .docx, .txt) to text, then has cold Opus subagents
  read them against that corpus's nine-dimension rubric and write batch notes
  with a provenance header. Per-document corpora get one subagent per document;
  batch corpora get one subagent over the whole pending set. Use when the user
  asks to extract documents, run extraction, build batch notes, or process a
  corpus. Fully automated; nothing is pasted into a browser.
---

# extract-voice-notes

Extraction end to end in the terminal. `extract.py` strips documents to text
deterministically; you (the orchestrator) spawn cold Opus subagents to do the
read and write the notes. The user never copies a prompt anywhere.

## Why cold subagents: do not skip this

The extraction read must happen in a subagent, never in this conversation:

- **No voice skill loaded.** If a voice skill (`paper-voice` or any other) is in
  context, it contaminates the read. A subagent starts cold.
- **No cross-corpus or cross-document bleed.** Each corpus is read on its own.
  In per-document mode each document gets its own subagent.

## Arguments

`/extract-voice-notes [--corpus NAME | --profile NAME] [doc_id ...] [--force]`

- No selector: the default profile's corpus.
- No doc ids: all pending documents (`corpus.py --pending` excludes processed
  and held-out documents).
- `--force doc_id ...`: re-extract named documents even if notes exist.

Pass the selector through to every script call below as `{sel}` (for example
`--corpus NAME`). Use `.venv/bin/python` if a `.venv` exists, else
`python3`.

## Procedure

1. **Read the corpus settings.** `python corpus.py {sel} --info` prints the
   corpus name, `extraction_mode`, the extraction template, the dimensions
   (rubric) file, and the working folders. Use these paths exactly.

2. **Resolve targets.** `python corpus.py {sel} --pending`, or the named ids. If
   the set is empty, say so and stop. Confirm with the user before spending
   tokens if more than about 3 documents would each get their own subagent.

3. **Strip.** `python extract.py {sel} {doc_id ...}` writes
   `{stripped_text_dir}/{doc}.txt` for each target (it reuses existing strips;
   add `--force` only when re-stripping is wanted).

4. **Sanity-check each strip (flag-only).** Read the head and a middle slice of
   each stripped file. Watch for interleaved columns, reference-list bleed,
   figure noise, near-empty output, and in .docx files letterhead, contact
   blocks, or tracked-change debris. Clean strips proceed. If a strip is
   corrupted, pause and flag that document; do not extract from garbage.
   Boilerplate that is merely present (a standing column title, a sign-off) is
   not corruption: the extraction instructions handle it.

5. **Extract.** Spawn subagents with `model: opus`. Pass each its exact model
   id (the id you launched, so the provenance header is accurate).

   **per_document mode**: one subagent per clean document, in parallel:

   > You are running as model `{model_id}`. Extract the writing voice from one
   > document. Read `{stripped_text_dir}/{doc}.txt` for the document,
   > `{extraction_template}` for the analysis instructions and output format,
   > and `{dimensions}` for the dimension definitions. Write your result to
   > `{batch_notes_dir}/notes_{doc}.md`, beginning with this exact header:
   > ```
   > ---
   > doc_id: {doc}
   > extracted: {YYYY-MM-DD}
   > model: {model_id}
   > ---
   > ```
   > Do not load or consult any voice or SKILL file; observe the voice from the
   > text alone. Reply with one line confirming the file was written.

   **batch mode**: ONE subagent over all clean target documents together:

   > You are running as model `{model_id}`. Extract the writing voice of one
   > author from {M} documents read together. Read `{dimensions}` (the rubric)
   > and `{extraction_template}` (instructions and output format) first. Then
   > read every document in full:
   > - `{stripped_text_dir}/{doc}.txt` (type: {type}) ... one line per document
   > Write your result to `{batch_notes_dir}/notes_batch_{YYYY-MM-DD}.md`
   > (append `_2`, `_3` if that file exists), beginning with this exact header:
   > ```
   > ---
   > doc_ids: [{doc}, {doc}, ...]
   > extracted: {YYYY-MM-DD}
   > model: {model_id}
   > ---
   > ```
   > Do not load or consult any voice or SKILL file; observe the voice from the
   > text alone. Reply with one line confirming the file was written.

   Get each document's type from `corpus_state.yaml` in the corpus root.

6. **Sync state.** `python corpus.py {sel}`. Its auto-mark reads each notes
   header (`doc_id` or `doc_ids`) and records the notes file, model, and date
   for every covered document.

7. **Report.** Per document: written / skipped / flagged. Do NOT run synthesis;
   that is `/synthesize-voice`, a separate deliberate step.

## Notes

- Everything under `corpora/` is gitignored local data.
- Extraction is token-expensive. Honor the user's targeting; never re-extract
  finished documents on a bare call.
