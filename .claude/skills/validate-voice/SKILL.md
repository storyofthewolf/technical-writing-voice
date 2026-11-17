---
name: validate-voice
description: Blind test of a built voice skill against held-out documents.
  For each held-out document, a cold subagent reduces it to a facts-only
  brief, then two cold subagents draft from that brief (one with the voice
  skill, one without), and the orchestrator assembles a blind side-by-side
  with the original for the author to judge. Use when the user asks to
  validate, test, or A/B a voice skill, or to check whether more corpus text
  is needed. Fully automated; the only manual step is the author's judgment.
---

# validate-voice

Measures whether a voice skill actually moves drafts toward the author, using
documents the skill never saw. Holding a document out (`corpus.py --set-holdout
DOC_ID on`) excludes it from extraction and synthesis, so set holdouts BEFORE
the first extraction of that corpus. A document whose notes are already in the
built skill is not a blind test; warn the user and stop if asked to validate on
one.

## Arguments

`/validate-voice [profile] [doc_id ...]`

Default targets: the corpus's held-out documents (`python corpus.py --profile
{p}` lists them under HELD OUT). Use `.venv/bin/python` if a `.venv` exists.
Read paths from `python corpus.py --profile {p} --info`. The built skill is the
profile's `output` path in `profiles.yaml` / `profiles.local.yaml`.

## Procedure

1. **Check.** The profile's skill file exists, each target is held out (or at
   least not `refined_into_skill_{p}`), and nothing in the target set was
   extracted. Otherwise stop and explain.

2. **Strip** the targets: `python extract.py --profile {p} {doc_id ...}`.

3. **Brief (one cold Opus subagent per document).**

   > Read `{stripped_text_dir}/{doc}.txt`. Write a facts-only brief to
   > `{validation_dir}/brief_{doc}.md` that a writer could draft the same piece
   > from without ever seeing it: the genre, the audience, the approximate
   > length in words, the purpose, and, in order, every point it makes with all
   > facts exact (figures, dates, names, titles, bill numbers, deadlines, asks,
   > links). Write each point as a neutral note in your own words. Do NOT copy
   > or closely paraphrase any sentence, do not describe tone or style, and do
   > not include openings, closings, or turns of phrase. Proper nouns and
   > numbers are the only text you may carry over. Reply with one line.

   Read each brief and check it carries no lifted phrasing. Fix by rerunning
   if it does.

4. **Draft (two cold Opus subagents per document, in parallel).** Neither may
   see the original or the stripped text.

   - **With skill:** "Read the voice skill at `{skill_path}` and follow it.
     Then read `{validation_dir}/brief_{doc}.md` and write the piece it
     describes, at about the stated length, to
     `{validation_dir}/draft_skill_{doc}.md`. Output only the piece. Do not
     read any other file in the corpus folder."
   - **Baseline:** the same, without the skill line, writing
     `{validation_dir}/draft_base_{doc}.md`.

5. **Assemble the blind comparison.** For each document, randomly order the
   two drafts as "Draft A" and "Draft B" (use Python's `random`), and write
   `{validation_dir}/compare_{doc}.md` with the original first, then Draft A,
   then Draft B, each under a plain heading and nothing else. Write the key
   (which draft used the skill) to `{validation_dir}/key_{doc}.md`. Do not show
   the key in chat.

6. **Report.** Give the user the compare file paths. Ask the author to judge,
   per document: which draft is closer to the original's voice, and what each
   draft gets wrong. Reveal the key only after they answer. Record their
   verdicts in `{validation_dir}/verdicts.md` (date, doc, choice, key, notes).
   If they give revision notes, offer `/synthesize-voice {p} revise "..."`.

## Notes

- Everything under `corpora/` is local-only. Never commit validation output.
- Read the verdicts as evidence: if the skill draft is not reliably preferred,
  or both drafts miss the same things, the corpus likely lacks that material.
- A held-out document can go back into the corpus after validation:
  `python corpus.py --profile {p} --set-holdout DOC_ID off`, then
  `/extract-voice-notes` and `/synthesize-voice {p} refine`.
