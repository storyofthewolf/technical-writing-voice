# DESIGN.md — pipeline architecture

This document records the architecture of the voice-skill pipeline as it runs
inside **Claude Code**, and the reasoning behind the load-bearing decisions.
`README.md` is the user-facing workflow; `CLAUDE.md` is the rules-to-preserve;
this file explains *why* the pieces are shaped the way they are.

---

## The three stages

```
   register            extract                    synthesize
   ────────            ───────                    ──────────
   corpus.py     →     /extract-corpus      →     /build-skill        →   skills/<profile>/SKILL.md
   (PDF/TXT)           (per-doc notes)            (one skill per profile)
```

1. **Registration** (`corpus.py`) — deterministic. Strips token counts, records
   document type and notes in `corpus_state.yaml`. No model involved.
2. **Extraction** (`/extract-corpus`) — per-document voice observations written to
   `batch_notes/notes_{doc}.md`. Model-driven, **sharded**.
3. **Synthesis** (`/build-skill`) — collapses notes into a purpose-specific
   `SKILL.md`. Model-driven, **whole-context**.

Stages 2 and 3 used to require a claude.ai copy-paste round-trip. Both now run in
the terminal. The Python scripts retain the **deterministic** work (stripping,
prompt assembly, applying); the **model** work is delegated to subagents.

---

## Profiles

The pipeline produces not one general SKILL.md but several narrow,
purpose-specific skills, defined in `profiles.yaml`. The first is `paper`: a slim
manuscript-writing voice (journal papers + proposals only) for Claude Code to
load when editing an Overleaf/LaTeX repo. A profile selects four things at once:
which synthesis template, which output format, which `corpus_types` feed it, and
where the result is written. Incorporation is tracked per profile via
`refined_into_skill_<profile>` flags, so building one skill never marks documents
done for another.

---

## Contamination is the organizing constraint

The single most important design force is **keeping the model's reads clean**. A
voice skill that already exists (e.g. `paper-voice`) will, if loaded in
context during extraction or synthesis, cause the model to *echo the voice the
skill already describes* instead of *observing it from the source*. This was
observed in practice: an earlier general-purpose voice skill contaminated
roughly half of extraction runs.

The defense, used at both model stages, is the **cold subagent**: a subagent
starts with a fresh context and does **not** inherit the parent conversation's
loaded skills. So the read happens with no voice model in its head.

The two stages apply this differently, and the difference matters:

| | Extraction | Synthesis |
|---|---|---|
| unit of work | one document | the whole corpus of notes |
| isolation shape | **many** subagents, one per doc | **one** subagent, all notes |
| why | also prevents cross-document bleed | must resolve cross-document conflicts in a single context — cannot shard |

Extraction shards because each document is independent and sharding adds a second
benefit (document B never bleeds into document A's notes). Synthesis must **not**
shard: its entire job is to weigh observations *against each other* across
documents, which requires holding them in one context. But it still runs cold,
because a from-scratch `--bootstrap` synthesized while the old skill is loaded
would be synthesizing partly from the skill it is supposed to rebuild.

---

## Model choice

**Opus by default for both model stages.** Extraction is the lossiest stage —
everything downstream is compression of the notes, so a missed or hallucinated
pattern is unrecoverable — and it requires discriminating the author's voice from
co-authors' within a single long document. Synthesis resolves subtle
cross-document conflicts. Both are capability-sensitive. The orchestrating skill
passes the exact model id to each subagent (rather than trusting the subagent's
self-knowledge) so the provenance record is accurate.

---

## Provenance tracking

Every `notes_{doc}.md` begins with a YAML header recording how it was made:

```
---
doc_id: wolf2025psj
extracted: 2026-06-23
model: claude-opus-4-8
---
```

The notes file is the **source of truth**. `corpus.py`'s `_auto_mark_done()`
reads the header on every status call and syncs `extraction_model` and
`extracted_date` into `corpus_state.yaml`, displaying `[model, date]` in the
PROCESSED listing. Headerless (legacy) notes show `model: unknown`. This makes
provenance automatic — no manual `--set-model` step — and it travels with the
notes even if extraction happened outside the skill.

---

## Stage 2 — extraction (`/extract-corpus`)

```
/extract-corpus [targets]
   1. resolve target set (all pending | doc IDs | --profile filter | --force)
        via: python corpus.py --pending [--pending-types ...]
        default: pending only — never silently re-extract finished docs
   2. python extract.py {doc}        — strip PDF → stripped_text/{doc}.txt
   3. sanity-check each strip         — flag-only gate; pause on garbage, others proceed
   4. one cold Opus subagent per clean doc:
        reads stripped_text/{doc}.txt + templates/extraction_prompt.md
        writes batch_notes/notes_{doc}.md with provenance header
        (no voice skill loaded; one doc only)
   5. python corpus.py                — auto-mark + provenance sync
   6. report: written / skipped / flagged. Does NOT run synthesis.
```

`templates/extraction_prompt.md` is the single analysis contract, shared by the
Claude Code path and any manual claude.ai run, so they cannot drift.

---

## Stage 3 — synthesis (`/build-skill`)

Scope: `--bootstrap` (from-scratch) and `--refine` (incremental). `--revision`
(authoritative freeform author edits) stays a manual `skill.py` command.

```
/build-skill [--profile paper] [--refine]
   1. ASSEMBLE (deterministic — skill.py, unchanged)
        bootstrap → all profile notes + synthesis template + skill template
        refine    → unrefined profile notes + current SKILL.md + refinement template
        → prompts/{bootstrap|refinement}_prompt_{profile}_{date}.md
   2. SYNTHESIZE (one cold Opus subagent — no voice skill loaded)
        reads the assembled prompt, produces the complete SKILL.md content,
        writes it to a response file
   3. APPLY (python skill.py --apply — automatic, with conflict-halt)
        bootstrap: always applies (conflict is structurally impossible)
        refine:    applies UNLESS the response contains "## CONFLICT REVIEW",
                   in which case STOP and surface the conflict for a human decision
        on apply: inject overrides, conflict-check, write live SKILL.md, mark state
```

### Why these choices

- **One cold subagent, all notes** — see the contamination table above. Synthesis
  cannot shard; it runs cold so a bootstrap is not contaminated by the skill it
  rebuilds.
- **Conflict is the review gate.** Bootstrap synthesizes with nothing to
  contradict, so it can never emit a `## CONFLICT REVIEW` block — it always
  applies. Refinement compares new notes against the current SKILL.md and emits a
  conflict block (and stops) only on a genuine contradiction. Auto-apply therefore
  pauses for a human in exactly the one case that warrants it, and nowhere else —
  no artificial review gate is needed.
- **`skill.py --apply` is reused untouched** — conflict detection, override
  injection, and per-profile state marking all already live there.

---

## Deferred: the fine-tuning layer

The synthesis output is the highest-stakes, most subjective artifact in the
pipeline, and it has quality failure modes that better *input* does not fix —
observed examples (TODO.md): adverb overuse, a "Note that" sentence-opening tic,
incorrect science terminology creeping into generated prose. These are
**post-synthesis** problems: a draft → critique-against-known-failure-modes →
revise loop.

This layer is **not yet designed**. The synthesis skill is deliberately built so
it can slot in **between step 2 (synthesize) and step 3 (apply)** without rework:

```
synthesize → [ fine-tune: critique vs. failure modes → revise ] → apply
```

**Override injection is its natural first tenant.** Overrides ("never use em
dashes") are post-hoc shaping in the same category as the failure-mode critiques.
They currently live inside `--apply` and stay there for now: removing them before
the fine-tuning layer exists would leave the live skill with no overrides in the
interim (a regression). When the fine-tuning layer is built, override injection
migrates into it.

---

## What stays deterministic (never delegated to a model)

- PDF/TXT stripping and token counting (`corpus.py`, `extract.py`)
- prompt assembly — gathering notes, filtering by profile, embedding templates
  (`skill.py`)
- applying a synthesized skill — conflict-check, override injection, writing the
  live file, marking corpus state (`skill.py --apply`)
- provenance sync from notes headers (`corpus.py`)

The model is delegated only the two reads it is uniquely needed for: observing
voice from a document (extraction) and resolving observations into a skill
(synthesis).
