---
name: build-skill
description: Synthesize or refine a profile's voice SKILL.md inside Claude Code.
  Assembles the synthesis prompt with skill.py, runs ONE cold Opus subagent over
  all the profile's batch notes to produce the complete SKILL.md, then applies it
  (with a conflict halt on refinement). Use when the user asks to build, bootstrap,
  synthesize, refine, or rebuild a voice skill / SKILL.md from the batch notes.
  Replaces the old claude.ai copy-paste synthesis loop. Does NOT handle extraction
  (use /extract-corpus) or freeform --revision (use skill.py directly).
---

# build-skill

Synthesize a purpose-specific voice `SKILL.md` from the batch notes, in the
terminal. This is the synthesis counterpart to `/extract-corpus`: `skill.py` does
the deterministic prompt assembly and the deterministic apply; a single cold Opus
subagent does the model work in between.

Scope: `--bootstrap` (from-scratch) and `--refine` (incremental). Freeform
`--revision` stays a manual `skill.py --revision` command and is out of scope here.

## Why ONE cold subagent (not many, and not the main conversation)

Synthesis must hold **all** the notes at once — its whole job is to weigh
observations *against each other* across documents and resolve conflicts. So
unlike extraction, it **cannot be sharded**: one subagent gets everything.

It must still run **cold** (a subagent, not this conversation): if a voice skill
such as `paper-voice` is loaded in context during synthesis, the model
synthesizes partly from the skill it is supposed to rebuild instead of purely from
the notes. A subagent starts fresh and does not inherit the parent's loaded
skills. Never run the synthesis read in the main conversation.

## Procedure

1. **Resolve the profile.** Default is the `default_profile` in `profiles.yaml`
   (`paper`). Honor `--profile NAME` if given.

2. **Assemble the prompt (deterministic).** Pick bootstrap vs. refine:
   - Bootstrap (default): `python skill.py --profile {name} --bootstrap --output {prompt_path}`
   - Refine: `python skill.py --profile {name} --refine --all --output {prompt_path}`

   Use a known staging path you control for `{prompt_path}` (e.g. under the
   scratchpad, or `prompts/`). `skill.py` gathers the profile's notes, filters by
   `corpus_types`, embeds the templates, and writes the full prompt there.

   If `skill.py` reports there is nothing to do (no processed notes for bootstrap,
   or no unrefined notes for refine), relay that and stop — there is nothing to
   synthesize.

3. **Synthesize — ONE cold Opus subagent.** Spawn a single subagent with
   `model: opus`. Give it a prompt that:
   - Tells it to read the assembled prompt file at `{prompt_path}` and follow the
     synthesis/refinement instructions embedded inside it exactly.
   - Tells it to write the **complete** resulting `SKILL.md` content to a response
     file `{response_path}` (a staging path, NOT the live skill path). It must
     output the whole file, not a summary or a diff.
   - Tells it NOT to load or consult any existing voice/SKILL file beyond what the
     assembled prompt already contains — synthesize from the notes in the prompt
     alone.
   - For refine: tells it that if it finds a genuine contradiction with the
     current SKILL.md, it must follow the embedded refinement instructions and
     emit a `## CONFLICT REVIEW` block instead of a finished SKILL.md.

4. **Apply (deterministic, with conflict halt).**
   `python skill.py --profile {name} --apply {response_path}`
   - **Bootstrap** always applies — a from-scratch synthesis has nothing to
     contradict, so a conflict is structurally impossible.
   - **Refine** applies UNLESS the response contains `## CONFLICT REVIEW`, in which
     case `--apply` prints the conflict and writes nothing. If that happens, STOP
     and surface the conflict block to the user for their decision — do not try to
     resolve it yourself.
   - On a successful apply, `skill.py` injects overrides, conflict-checks, writes
     the live `skills/{name}/SKILL.md`, and marks the profile's docs incorporated.

5. **Report.** Tell the user which profile was built, bootstrap vs. refine, where
   the live skill landed, and how many documents were marked incorporated. If a
   conflict halted a refine, show the conflict and the resolution options
   (`skill.py --apply` after editing notes, or re-run treating it as register
   variation). Suggest reviewing the result with `git diff` if the skill path is
   tracked, or by reading `skills/{name}/SKILL.md`.

## Subagent prompt template

Roughly (fill in braces):

> You are synthesizing a writer's voice SKILL.md. Read the assembled prompt at
> `{prompt_path}` — it contains corpus metadata, all the batch notes for this
> profile, the output-format template, and the full synthesis (or refinement)
> instructions. Follow those embedded instructions exactly. Write the COMPLETE
> resulting SKILL.md content to `{response_path}` — the entire file, ready to
> apply, with nothing omitted and no commentary before or after it. Do not load or
> consult any existing voice or SKILL file beyond what the prompt contains;
> synthesize only from the notes in the prompt. [Refine only:] If you find a
> genuine contradiction with the current SKILL.md, emit a `## CONFLICT REVIEW`
> block per the embedded refinement instructions instead of a finished file.

## Notes

- `skill.py --apply` is reused untouched — it owns conflict detection, override
  injection, and per-profile state marking.
- **Override injection currently happens in `--apply`.** A future fine-tuning layer
  (draft → critique against known failure modes → revise) will sit between steps 3
  and 4 and will eventually own override injection. This skill is built to not
  foreclose that: it stops at a complete synthesized file and applies it as a
  discrete step. See DESIGN.md.
- Extraction is a separate skill (`/extract-corpus`). Run it first if there are
  unprocessed documents you want included.
