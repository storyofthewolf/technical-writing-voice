---
name: extract-corpus
description: Run voice extraction over the corpus inside Claude Code. Strips any
  pending PDFs to text, then spawns one isolated Opus subagent per document to
  read the stripped text against the nine voice dimensions and write
  batch_notes/notes_{doc}.md with a provenance header. Use when the user asks to
  extract documents, run extraction, build batch notes, or process the corpus.
  Replaces the old claude.ai copy-paste loop.
---

# extract-corpus

Orchestrate voice extraction end to end in the terminal. This is the workflow
that used to require pasting `prompt_{doc}.md` into claude.ai and saving the
response by hand. Now `extract.py` does the deterministic stripping and you
(the orchestrator) spawn an isolated Opus subagent per document to do the read.

## Why isolation matters — do not skip this

The extraction read must happen in a **cold subagent context**, one per document:

- **No voice skill loaded.** If `eric-wolf-paper-voice` (or any voice skill) is in
  context during extraction, it contaminates the read — the analysis starts
  echoing the voice the skill already described instead of observing it fresh.
  A subagent starts cold and does not inherit the parent's loaded skills.
- **No cross-document bleed.** One subagent per document means document B's
  patterns never leak into document A's notes.

Never do the extraction read in this main conversation. Always delegate to a
subagent. This is the whole reason the design uses subagents.

## Targeting (resolve the document set first)

Parse the invocation argument to decide which documents to extract. Default to
**pending only** — never re-extract a document that already has notes unless the
user explicitly names it or passes `--force`.

- `/extract-corpus` — all pending documents (registered, no `notes_{doc}.md` yet).
  Get the list with: `python corpus.py --pending`
- `/extract-corpus <doc_id> [<doc_id> ...]` — exactly these documents.
- `/extract-corpus --profile <name>` — only pending documents whose type is in
  that profile's `corpus_types`. Read the types from `profiles.yaml`, then:
  `python corpus.py --pending --pending-types <type> [<type> ...]`
- `/extract-corpus --force <doc_id> ...` — re-extract named documents even if
  notes already exist (e.g. to redo with a better model).

If the resolved set is empty, say so and stop — there is nothing to extract.

## Procedure

1. **Resolve targets** per the rules above. Confirm the list to the user before
   spending tokens if the set is large (more than ~3 documents).

2. **Strip to text.** For each target lacking `stripped_text/{doc}.txt`, run
   `python extract.py {doc_id}` to produce it. (`extract.py` also writes a
   `prompt_{doc}.md`; ignore that file in this flow — it is the claude.ai
   artifact. You only need the stripped text.)

3. **Sanity-check each strip (flag-only gate).** Read the head and a middle slice
   of each `stripped_text/{doc}.txt`. Watch for: multi-column text interleaved
   line-by-line, reference-list bleed, figure/axis-label noise, or near-empty
   output. If a strip looks clean, proceed automatically. If a strip looks
   corrupted, **pause and flag that document to the user** — do not extract from
   garbage. Clean documents in the same batch still proceed.

4. **Extract — one Opus subagent per clean document.** For each document, spawn a
   subagent with `model: opus`. Give the subagent a prompt that:
   - States its model id explicitly (you know you launched Opus — pass the exact
     id, e.g. `claude-opus-4-8`, so the provenance header is accurate rather than
     relying on the subagent's self-knowledge).
   - Tells it to read `stripped_text/{doc}.txt` and the analysis contract in
     `templates/extraction_prompt.md`.
   - Tells it to write the result to `batch_notes/notes_{doc}.md`, beginning with
     the required provenance header:
     ```
     ---
     doc_id: {doc}
     extracted: {today YYYY-MM-DD}
     model: {the exact model id you passed}
     ---
     ```
   - Tells it to follow `templates/extraction_prompt.md` exactly for the body and
     to return only a one-line confirmation (the notes file is the real output).

   Independent documents can be extracted in parallel — spawn their subagents in
   the same turn.

5. **Sync state.** After the notes files are written, run `python corpus.py`. Its
   auto-mark reads each notes header and records `extraction_model` and
   `extracted_date` into `corpus_state.yaml`, then prints the status with
   provenance (e.g. `[opus-4-8, 2026-06-23]`).

6. **Report.** Tell the user, per document: written / skipped (already had notes) /
   flagged (bad strip). Point out anything that needs their eyes. Do **not** run
   synthesis — building/refining the SKILL.md is a separate, deliberate step
   (`skill.py --bootstrap` / `--refine`).

## Subagent prompt template

Use a prompt of roughly this shape for each extraction subagent (fill in braces):

> You are running as model `{model_id}`. Extract the technical writing voice from
> one document. Read `stripped_text/{doc}.txt` for the document text and
> `templates/extraction_prompt.md` for the full analysis instructions and output
> format. Analyze the document against all nine dimensions exactly as that file
> specifies. Write your result to `batch_notes/notes_{doc}.md`. The file must begin
> with this exact header, then the notes body per the template:
> ```
> ---
> doc_id: {doc}
> extracted: {date}
> model: {model_id}
> ---
> ```
> Do not load or consult any voice/SKILL file — observe the voice fresh from the
> text alone. Reply with one line confirming the file was written.

## Notes

- Extraction is profile-agnostic: the notes feed any profile. `--profile` here is
  only a token-budgeting filter on which pending docs to read now.
- `batch_notes/` and `stripped_text/` are gitignored local working data.
- Extraction is token-expensive (a fresh Opus read per document). Honor the
  user's targeting; never silently extract the whole corpus on a bare call if
  most of it is already done — `--pending` already excludes finished docs.
