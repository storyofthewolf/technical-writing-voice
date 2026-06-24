# CLAUDE.md — technical-writing-voice

This project builds **purpose-specific voice skills** from a corpus of the author's own technical documents. The pipeline extracts voice observations document-by-document, then synthesizes them into one or more narrow `SKILL.md` files — one per writing context — and refines each incrementally as documents are added.

**Profiles.** Rather than a single general-purpose `SKILL.md`, the pipeline produces a separate skill per writing purpose, defined in `profiles.yaml`. The first and primary profile is `paper`: a slim manuscript-writing voice (journal papers and proposals only) built for Claude Code to load when editing a GitHub-backed Overleaf/LaTeX repository. It governs prose voice and argument structure only — LaTeX, `.bib`, and figure markup are deferred to Claude's standard best practices (`latex_policy: defer`). Informal registers (emails, letters, statements) are deliberately out of scope for the paper profile, since that "personal touch" writing resists AI assistance; formal manuscript prose is the high-value target.

See `README.md` for full workflow documentation.

---

## Scripts

| Script | Role |
|--------|------|
| `corpus.py` | Register documents, update metadata, report status. Auto-marks documents done when `batch_notes/notes_{doc_id}.md` appears. |
| `extract.py` | Strip PDFs to plain text (`stripped_text/`), generate extraction prompts (`batch_notes/prompt_*.md`). |
| `skill.py` | Profile-aware. Generate bootstrap, refinement, and revision prompts; apply Claude's responses to the selected profile's `SKILL.md`; inject `## Manual Overrides` section. Reads `profiles.yaml`. |
| `overrides.py` | Manage `overrides.yaml` via `list` / `add` / `remove` subcommands. |
| `archive.py` | Snapshot pipeline state to `archive/run_TIMESTAMP[_label]/`; optional `--reset soft` or `--reset full`. |

---

## Key files

- `profiles.yaml` — defines each purpose-specific skill (name, purpose, source `corpus_types`, synthesis template, output path, token budget, `latex_policy`) plus `default_profile`. Add a new entry to create a new skill — no script changes needed. If absent, `skill.py` falls back to legacy single-`SKILL.md` behavior.
- `corpus_state.yaml` — tracks all registered documents and their processing state. Incorporation is tracked **per profile** via `refined_into_skill_<profile>` flags (legacy mode uses the original `refined_into_skill`).
- `overrides.yaml` — manual editorial directives; never touched by `archive.py`; injected into the selected profile's `SKILL.md` by `skill.py --apply` or `skill.py --overrides`
- `skills/<profile>/SKILL.md` — the built voice skill for each profile (e.g. `skills/paper/SKILL.md`). Copy into `.claude/skills/` when ready for Claude Code to load.
- `templates/` — LLM instruction templates embedded in generated prompts; not modified by scripts
  - `extraction_prompt.md` — voice extraction instructions
  - `synthesis_prompt.md` — general (legacy) first-time synthesis instructions
  - `synthesis_paper.md` — slim, manuscript-register synthesis for the `paper` profile (single register, hard token budget, LaTeX deferred)
  - `refinement_prompt.md` — incremental refinement instructions
  - `revision_prompt.md` — freeform manual revision instructions
- `core/` — stable definitions; not modified by scripts or Claude
  - `EVALUATION_DIMENSIONS.md` — the nine voice dimensions
  - `SKILL_TEMPLATE.md` — general output format
  - `SKILL_TEMPLATE_PAPER.md` — slim output format for the `paper` profile

---

## skill.py command interface

`--profile NAME` selects the profile from `profiles.yaml`; it defaults to `default_profile` (`paper`) when omitted. All actions operate on the selected profile's output path and its `corpus_types`-filtered notes.

```
python skill.py [--profile NAME] --bootstrap                  # synthesis prompt from the profile's notes
python skill.py [--profile NAME] --refine NOTES_FILE          # refinement prompt for a specific notes file
python skill.py [--profile NAME] --refine --all              # refinement prompt for the profile's unrefined notes
python skill.py [--profile NAME] --revision INSTRUCTIONS_FILE # revision prompt from freeform instructions file
python skill.py [--profile NAME] --apply CLAUDE_RESPONSE      # write Claude's response to the profile's SKILL.md
python skill.py [--profile NAME] --overrides                  # inject overrides.yaml into the profile's SKILL.md
python skill.py --output FILE                                 # write prompt to FILE instead of prompts/
```

---

## Design rules to preserve

**Profiles drive the output target.** `skill.py` reads `profiles.yaml` and resolves a `Profile` (default `paper`). Every action writes to that profile's `output` path (e.g. `skills/paper/SKILL.md`), filters notes by the profile's `corpus_types`, and uses the profile's synthesis template and skill template. The bootstrap prompt injects a "Profile directives" block (skill name, purpose, token budget, LaTeX policy) so Claude builds the right skill. If `profiles.yaml` is absent, a legacy profile reproduces the original single-`SKILL.md` behavior unchanged.

**Incorporation is per profile.** `--apply` marks a document incorporated by setting `refined_into_skill_<profile>` (e.g. `refined_into_skill_paper`), not a global flag. Building one profile never marks documents as done for another. Legacy mode uses the original `refined_into_skill`.

**All documents contribute evenly — no weighting.** There is no confidence rating, no token weighting, and no influence math. `corpus.py` records `prose_tokens` as informational corpus size only. Synthesis and refinement prompts instruct Claude to weigh a pattern by how consistently it recurs across documents, never by token count or any per-document score. The removed pieces: `confidence`/`--set-confidence`/`validate_confidence` in `corpus.py`, `--priority` in `extract.py`, and `effective_tokens`/`compute_new_doc_influence` in `skill.py`. Do not reintroduce per-document weighting.

**Overrides are post-processing only.** `overrides.py` manages `overrides.yaml`. `skill.py --apply` appends overrides as a numbered `## Manual Overrides` section at the end of the profile's `SKILL.md` after writing Claude's response. `skill.py --overrides` injects them into an existing profile `SKILL.md` without a Claude response. Overrides are never included in prompts sent to Claude — they are invisible to the LLM.

**Revision instructions are authoritative.** `skill.py --revision` generates a prompt from a freeform instructions file and the current `SKILL.md`. Claude applies the instructions without conflict detection — the author's directives take precedence by definition. The revision prompt is saved to `prompts/revision_prompt_DATE.md`; the instructions file itself is not saved separately.

**Auto-mark on status.** `corpus.py`'s `cmd_status()` calls `_auto_mark_done()` first. It scans unprocessed documents, checks whether `batch_notes/notes_{doc_id}.md` exists, and marks any found as `processed=True` with `batch_notes_file` and `processed_date` set. No manual `--mark-done` command needed.

**Archive never touches overrides.** `archive.py` copies `SKILL.md`, `batch_notes/`, `prompts/`, and `corpus_state.yaml`. It never reads, copies, or modifies `overrides.yaml`. Overrides persist across all reset modes.

**Conflict detection stops the apply.** If Claude's response contains `## CONFLICT REVIEW`, `skill.py --apply` prints the conflict and exits without writing the profile's `SKILL.md` or updating state. Conflict detection is skipped for `--revision` responses.

**The profile's output path is the target.** `skill.py --apply` writes to the resolved profile's `output` path (creating parent directories as needed). There is no `SKILL_FILE` argument — the path comes from `profiles.yaml`, defaulting to `skills/paper/SKILL.md`.

**Paths resolve from script location.** All scripts use `Path(__file__).parent` as the base so they work when invoked from any directory.

---

## Current script inventory

| Script | Status |
|--------|--------|
| `corpus.py` | Stable |
| `extract.py` | Stable |
| `skill.py` | Stable — replaced `refine.py` |
| `overrides.py` | Stable |
| `archive.py` | Stable |
