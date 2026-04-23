# CLAUDE.md — technical-writing-voice

This project builds a personal voice model (`SKILL.md`) from a corpus of the author's own technical documents. The pipeline extracts voice observations document-by-document, synthesizes them into a structured skill file, and refines the model incrementally as new documents are added.

See `README.md` for full workflow documentation.

---

## Scripts

| Script | Role |
|--------|------|
| `corpus.py` | Register documents, update metadata, report status. Auto-marks documents done when `batch_notes/notes_{doc_id}.md` appears. |
| `extract.py` | Strip PDFs to plain text (`stripped_text/`), generate extraction prompts (`batch_notes/prompt_*.md`). |
| `refine.py` | Generate bootstrap and refinement prompts; apply Claude's responses to `SKILL.md`; append `## Manual Overrides` section. |
| `overrides.py` | Manage `overrides.yaml` via `list` / `add` / `remove` subcommands. |
| `archive.py` | Snapshot pipeline state to `archive/run_TIMESTAMP[_label]/`; optional `--reset soft` or `--reset full`. |

---

## Key files

- `corpus_state.yaml` — tracks all registered documents and their processing state
- `overrides.yaml` — manual editorial directives; never touched by `archive.py`; injected into `SKILL.md` by `refine.py --apply`
- `SKILL.md` — the output voice model; add to the author's Claude Project knowledge
- `templates/` — LLM instruction templates embedded in generated prompts; not modified by scripts
- `core/` — stable definitions (dimensions, template); not modified by scripts or Claude

---

## Design rules to preserve

**Overrides are post-processing only.** `overrides.py` manages `overrides.yaml`. `refine.py --apply` appends overrides as a numbered `## Manual Overrides` section at the end of `SKILL.md` after writing Claude's response. Overrides are never included in prompts sent to Claude — they are invisible to the LLM.

**Auto-mark on status.** `corpus.py`'s `cmd_status()` calls `_auto_mark_done()` first. It scans unprocessed documents, checks whether `batch_notes/notes_{doc_id}.md` exists, and marks any found as `processed=True` with `batch_notes_file` and `processed_date` set. No manual `--mark-done` command needed.

**Archive never touches overrides.** `archive.py` copies `SKILL.md`, `batch_notes/`, and `corpus_state.yaml`. It never reads, copies, or modifies `overrides.yaml`. Overrides persist across all reset modes.

**Conflict detection stops the apply.** If Claude's response contains `## CONFLICT REVIEW`, `refine.py --apply` prints the conflict and exits without writing `SKILL.md` or updating state.

**Paths resolve from script location.** All scripts use `Path(__file__).parent` as the base so they work when invoked from any directory.

---

## Changes made 2026-04-23

### corpus.py
- Added `_auto_mark_done(state)` helper called at the start of `cmd_status()`. Scans documents where `processed=False`, checks for `batch_notes/notes_{doc_id}.md`, marks found documents done, saves state, and prints a notice per auto-marked document.

### overrides.py (new)
- Standalone CLI managing `overrides.yaml`. Subcommands: `list`, `add TEXT [--category CAT]`, `remove ID`. Each entry has `id` (auto-incremented `ov001`, `ov002`, …), `instruction`, `added` date, and optional `category`. Under 150 lines, stdlib + pyyaml.

### refine.py
- Added `OVERRIDES_FILE` path constant.
- Added `load_overrides()` and `_overrides_block(overrides)` helpers. Block format: `## Manual Overrides` header followed by a numbered list (`1. instruction`).
- `cmd_apply()`: after writing `SKILL.md`, reads `overrides.yaml`. If a `## Manual Overrides` section already exists in the file, replaces it (regex from marker to EOF). If absent and overrides are non-empty, appends the block after a `---` separator.
- Overrides are **not** injected into bootstrap or refinement prompts — post-processing only.

### archive.py (new)
- Copies `SKILL.md`, `batch_notes/`, `corpus_state.yaml` into `archive/run_YYYY-MM-DD_HHMMSS[_label]/`. Never copies `overrides.yaml`.
- `--reset soft`: deletes `SKILL.md`, clears `refined_into_skill` and `refined_date` on all docs, leaves `processed` and notes untouched.
- `--reset full`: deletes `SKILL.md` and `batch_notes/`, resets all docs to `processed=False`, `refined_into_skill=False`, clears `batch_notes_file`, `processed_date`, `refined_date`.
- Under 150 lines, stdlib + pyyaml.

### templates/refinement_prompt.md
- No net change: an instruction added in an earlier session (preserve `## Manual Overrides` verbatim) was removed in the same session when the design changed to post-processing-only injection.
