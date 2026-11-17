---
name: synthesize-voice
description: Build, refine, or revise a profile's voice SKILL.md inside Claude
  Code. Assembles the prompt with skill.py, runs ONE cold Opus subagent to
  write the complete SKILL.md, then applies it (with a conflict halt on
  refinement). Modes - bootstrap (from all notes), refine (fold in new notes),
  revise (apply the user's plain-language edits). Use when the user asks to
  build, bootstrap, synthesize, refine, rebuild, revise, or adjust a voice skill.
  Fully automated; nothing is pasted into a browser. Does NOT extract (use
  /extract-voice-notes).
---

# synthesize-voice

Turns batch notes (or the user's revision notes) into the finished voice
skill, in the terminal. `skill.py` assembles the prompt and applies the result
deterministically; one cold Opus subagent does the model work in between.

## Arguments

`/synthesize-voice [profile] [bootstrap | refine | revise "<instructions>"]`

- `profile`: a name from `profiles.yaml` / `profiles.local.yaml`; default is
  `default_profile`.
- Mode: `bootstrap` if the profile has no built skill yet; otherwise ask
  whether the user wants `refine` (new notes exist) or a full `bootstrap`
  rebuild. `revise` takes the user's instructions, verbatim, from the
  invocation or from their message.

Use `.venv/bin/python` if a `.venv` exists, else `python3`. Stage prompt and
response files in the scratchpad (or the corpus's `prompts/` folder).

## Why ONE cold subagent

Synthesis weighs observations across all documents at once, so it cannot be
sharded. It must still run cold: if a voice skill is loaded in context, the
model rebuilds partly from that skill instead of from the notes. Never do the
synthesis or revision in the main conversation.

## Procedure

1. **Assemble the prompt.**
   - Bootstrap: `python skill.py --profile {p} --bootstrap --output {prompt}`
   - Refine: `python skill.py --profile {p} --refine --all --output {prompt}`
   - Revise: write the user's instructions verbatim to `{instructions}`, then
     `python skill.py --profile {p} --revision {instructions} --output {prompt}`

   If `skill.py` reports nothing to do, relay it and stop.

2. **One cold Opus subagent** (`model: opus`):

   > You are updating a writer's voice SKILL.md. Read the assembled prompt at
   > `{prompt}`. It contains everything you need and the instructions to follow
   > exactly. Write the COMPLETE resulting SKILL.md to `{response}`: the whole
   > file, nothing omitted, no commentary before or after. Do not load or
   > consult any voice or SKILL file beyond what the prompt contains.
   > [Refine only:] If you find a genuine contradiction with the current
   > SKILL.md, emit a `## CONFLICT REVIEW` block per the embedded instructions
   > instead of a finished file.

3. **Apply.** `python skill.py --profile {p} --apply {response}`
   - Bootstrap and revise always apply.
   - Refine applies unless the response contains `## CONFLICT REVIEW`; then
     nothing is written. STOP and show the conflict to the user for a decision.
   - Apply injects the corpus's overrides, writes the profile's `output` path,
     and marks the profile's documents incorporated.

4. **Report.** Profile, mode, where the skill landed, documents incorporated.
   Show the change: `git diff` if the output is tracked (e.g.
   `skills/paper/SKILL.md`), else a diff against the previous version (archive
   first with `python archive.py --profile {p} --label before_{mode}` if the
   user wants a restorable snapshot). Skills written under `corpora/` are
   local-only and must never be committed.

## Notes

- Revision instructions are authoritative: no conflict check.
- Overrides live per corpus in `corpora/<corpus>/overrides.yaml`
  (`python overrides.py --corpus NAME add "..."`). They are appended at apply
  time and never sent to the subagent.
- Profiles whose output is under `corpora/` (for example another author's
  voice) are not installed with skill-sync. Deliver them as files.
