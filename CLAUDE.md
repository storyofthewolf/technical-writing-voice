# CLAUDE.md — technical-writing-voice

This project builds a personal voice model (`SKILL.md`) from a corpus of the author's own technical documents. The pipeline extracts voice observations document-by-document, synthesizes them into a structured skill file, and refines the model incrementally as new documents are added.

See `README.md` for full workflow documentation.

---

## Scripts

| Script | Role |
|--------|------|
| `corpus.py` | Register documents, update metadata, report status. Auto-marks documents done when `batch_notes/notes_{doc_id}.md` appears. |
| `extract.py` | Strip PDFs to plain text (`stripped_text/`), generate extraction prompts (`batch_notes/prompt_*.md`). |
| `skill.py` | Generate bootstrap, refinement, and revision prompts; apply Claude's responses to `SKILL.md`; inject `## Manual Overrides` section. |
| `overrides.py` | Manage `overrides.yaml` via `list` / `add` / `remove` subcommands. |
| `archive.py` | Snapshot pipeline state to `archive/run_TIMESTAMP[_label]/`; optional `--reset soft` or `--reset full`. |

---

## Key files

- `corpus_state.yaml` — tracks all registered documents and their processing state
- `overrides.yaml` — manual editorial directives; never touched by `archive.py`; injected into `SKILL.md` by `skill.py --apply` or `skill.py --overrides`
- `SKILL.md` — the output voice model; add to the author's Claude Project knowledge
- `templates/` — LLM instruction templates embedded in generated prompts; not modified by scripts
  - `extraction_prompt.md` — voice extraction instructions
  - `synthesis_prompt.md` — first-time SKILL.md synthesis instructions
  - `refinement_prompt.md` — incremental refinement instructions
  - `revision_prompt.md` — freeform manual revision instructions
- `core/` — stable definitions (dimensions, template); not modified by scripts or Claude

---

## skill.py command interface

```
python skill.py --bootstrap                      # synthesis prompt from all processed notes
python skill.py --refine NOTES_FILE              # refinement prompt for a specific notes file
python skill.py --refine --all                   # refinement prompt for all unrefined notes
python skill.py --revision INSTRUCTIONS_FILE     # revision prompt from freeform instructions file
python skill.py --apply CLAUDE_RESPONSE          # write Claude's response to SKILL.md
python skill.py --overrides                      # inject overrides.yaml into existing SKILL.md
python skill.py --output FILE                    # write prompt to FILE instead of prompts/
```

---

## Design rules to preserve

**Overrides are post-processing only.** `overrides.py` manages `overrides.yaml`. `skill.py --apply` appends overrides as a numbered `## Manual Overrides` section at the end of `SKILL.md` after writing Claude's response. `skill.py --overrides` injects them into an existing `SKILL.md` without a Claude response. Overrides are never included in prompts sent to Claude — they are invisible to the LLM.

**Revision instructions are authoritative.** `skill.py --revision` generates a prompt from a freeform instructions file and the current `SKILL.md`. Claude applies the instructions without conflict detection — the author's directives take precedence by definition. The revision prompt is saved to `prompts/revision_prompt_DATE.md`; the instructions file itself is not saved separately.

**Auto-mark on status.** `corpus.py`'s `cmd_status()` calls `_auto_mark_done()` first. It scans unprocessed documents, checks whether `batch_notes/notes_{doc_id}.md` exists, and marks any found as `processed=True` with `batch_notes_file` and `processed_date` set. No manual `--mark-done` command needed.

**Archive never touches overrides.** `archive.py` copies `SKILL.md`, `batch_notes/`, `prompts/`, and `corpus_state.yaml`. It never reads, copies, or modifies `overrides.yaml`. Overrides persist across all reset modes.

**Conflict detection stops the apply.** If Claude's response contains `## CONFLICT REVIEW`, `skill.py --apply` prints the conflict and exits without writing `SKILL.md` or updating state. Conflict detection is skipped for `--revision` responses.

**SKILL.md is always the implied target.** `skill.py --apply` always writes to `SKILL.md` in the project root. There is no `SKILL_FILE` argument — the path is hardcoded.

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
