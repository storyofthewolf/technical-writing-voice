# CLAUDE.md — technical-writing-voice

This project builds **purpose-specific voice skills** from a corpus of the author's own technical documents. The pipeline extracts voice observations document-by-document, then synthesizes them into one or more narrow `SKILL.md` files — one per writing context — and refines each incrementally as documents are added.

**Profiles.** Rather than a single general-purpose `SKILL.md`, the pipeline produces a separate skill per writing purpose, defined in `profiles.yaml`. The first and primary profile is `paper`: a slim manuscript-writing voice (journal papers and proposals only) built for Claude Code to load when editing a GitHub-backed Overleaf/LaTeX repository. It governs prose voice and argument structure only — LaTeX, `.bib`, and figure markup are deferred to Claude's standard best practices (`latex_policy: defer`). The paper profile's **corpus** is manuscripts only: emails, letters, and statements are deliberately excluded as source documents, since that "personal touch" register resists AI assistance. Its **use** is broader. Since commit 2524493 one `paper-voice` skill serves both Claude Code (Overleaf manuscripts) and claude.ai (professional emails, letters, statements), because Claude Code also loads claude.ai account skills and two same-named copies competed. The skill's instruction block decides the kind of writing first and carries only the sentence-level voice over to non-manuscript writing; it never invents an informal register.

**Corpora.** Since 2026-11 the repo serves more than one author. Each author's documents live in a gitignored workspace `corpora/<name>/` (state, notes, stripped text, prompts, archive, overrides, validation), resolved by `paths.py` from `--corpus` or `--profile`. Eric's corpus is `wolf`. A second author's corpus and profile (association government-relations writing, `.docx` member columns) are defined only in the gitignored `profiles.local.yaml` and build their skill under `corpora/`, so neither the data nor the skill reaches GitHub. Do not name that author or client in tracked files.

See `README.md` for full workflow documentation.

---

## Scripts

| Script | Role |
|--------|------|
| `paths.py` | Resolves the corpus workspace (`--corpus` / `--profile` / default profile) and merges `profiles.local.yaml` over `profiles.yaml`. Shared by every script. |
| `corpus.py` | Register documents (.pdf/.docx/.txt), update metadata, set holdouts, report status, print `--info` for the project skills. Auto-marks documents done when a notes file covers them (`notes_{doc}.md`, or a batch file whose header lists `doc_ids`). |
| `extract.py` | Strip documents to plain text in the corpus's `stripped_text/`. Strip-only: no prompt files, no `--mark-done`. |
| `skill.py` | Profile-aware. Generate bootstrap, refinement, and revision prompts; apply responses to the profile's `SKILL.md`; inject the corpus's overrides. |
| `overrides.py` | Manage a corpus's `overrides.yaml` via `list` / `add` / `remove`. |
| `archive.py` | Profile-aware. Snapshot to `corpora/<corpus>/archive/run_TIMESTAMP_<profile>[_label]/`; optional `--reset soft` or `--reset full` scoped to that profile. |

---

## Key files

- `profiles.yaml` — defines `corpora` (root, `doc_types`, `dimensions` rubric, `extraction_template`, `extraction_mode`) and `profiles` (corpus, skill name, optional `writer_name`, purpose, `corpus_types`, synthesis and skill templates, output path, token budget, `latex_policy` or `format_policy`) plus `default_profile`. Required. `profiles.local.yaml` (gitignored) is merged over it for local-only entries.
- `corpora/<name>/corpus_state.yaml` — that corpus's documents and processing state. Incorporation is tracked **per profile** via `refined_into_skill_<profile>` flags; `holdout: true` excludes a document from extraction and synthesis. Stored paths are relative to the corpus root.
- `corpora/<name>/overrides.yaml` — that corpus's manual editorial directives; never touched by `archive.py`; injected by `skill.py --apply` or `--overrides`.
- `skills/<profile>/SKILL.md` — the built voice skill for each profile (e.g. `skills/paper/SKILL.md`). Tracked in git; installed to `~/.claude/skills/` by skill-sync (registry: `~/Research/tools/skill-sync/skills.toml`).
- `templates/` — LLM instruction templates embedded in generated prompts; not modified by scripts
  - `extraction_prompt.md` — per-document voice extraction instructions (science)
  - `extraction_batch.md` — domain-neutral batch extraction (one subagent over many short documents, recurrence counts)
  - `synthesis_advocacy.md` — synthesis for association / government-relations profiles
  - `synthesis_prompt.md` — general first-time synthesis instructions (default for profiles that don't set their own `synthesis_template`)
  - `synthesis_paper.md` — slim, manuscript-register synthesis for the `paper` profile (single register, hard token budget, LaTeX deferred)
  - `refinement_prompt.md` — incremental refinement instructions
  - `revision_prompt.md` — freeform manual revision instructions
- `core/` — stable definitions; not modified by scripts or Claude
  - `EVALUATION_DIMENSIONS.md` — the nine voice dimensions, science rubric (kept byte-identical for the paper profile)
  - `domains/EVALUATION_DIMENSIONS_ADVOCACY.md` — the same nine dimensions for association advocacy writing
  - `SKILL_TEMPLATE_ADVOCACY.md` — output format for advocacy profiles
  - `SKILL_TEMPLATE.md` — general output format
  - `SKILL_TEMPLATE_PAPER.md` — slim output format for the `paper` profile

---

## skill.py command interface

`--profile NAME` selects the profile (and so its corpus); it defaults to `default_profile` (`paper`). All actions operate on the profile's output path and its `corpus_types`-filtered, non-holdout notes. Prompts default to the corpus's `prompts/`.

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

**Profiles drive the output target.** `skill.py` reads `profiles.yaml` and resolves a `Profile` (default `paper`). Every action writes to that profile's `output` path (e.g. `skills/paper/SKILL.md`), filters notes by the profile's `corpus_types`, and uses the profile's synthesis template and skill template. The bootstrap prompt injects a "Profile directives" block (skill name, purpose, token budget, LaTeX policy) so Claude builds the right skill. `profiles.yaml` is required; `skill.py` exits with an error if it is absent.

**Incorporation is per profile.** `--apply` marks a document incorporated by setting `refined_into_skill_<profile>` (e.g. `refined_into_skill_paper`), not a global flag. Building one profile never marks documents as done for another. `corpus.py --status` discovers these flags directly from the document data (no `profiles.yaml` coupling) and reports an incorporation count per profile.

**All documents contribute evenly — no weighting.** There is no confidence rating, no token weighting, and no influence math. `corpus.py` records `prose_tokens` as informational corpus size only. Synthesis and refinement prompts instruct Claude to weigh a pattern by how consistently it recurs across documents, never by token count or any per-document score. The removed pieces: `confidence`/`--set-confidence`/`validate_confidence` in `corpus.py`, `--priority` in `extract.py`, and `effective_tokens`/`compute_new_doc_influence` in `skill.py`. Do not reintroduce per-document weighting.

**Corpora are isolated.** All working data for an author lives under `corpora/<name>/`, resolved through `paths.py`. Never write corpus data, notes, or a local-only profile's skill outside `corpora/`, and never commit `corpora/` or `profiles.local.yaml`. The paper profile's built skill stays at the tracked `skills/paper/SKILL.md` (skill-sync installs from there).

**Overrides are post-processing only.** `overrides.py` manages the corpus's `overrides.yaml`. `skill.py --apply` appends overrides as a numbered `## Manual Overrides` section at the end of the profile's `SKILL.md` after writing Claude's response. `skill.py --overrides` injects them into an existing profile `SKILL.md` without a Claude response. Overrides are never included in prompts sent to Claude — they are invisible to the LLM.

**Revision instructions are authoritative.** `skill.py --revision` generates a prompt from a freeform instructions file and the current `SKILL.md`. Claude applies the instructions without conflict detection — the author's directives take precedence by definition. The revision prompt is saved to `prompts/revision_prompt_DATE.md`; the instructions file itself is not saved separately.

**Auto-mark on status.** `corpus.py`'s `cmd_status()` (and `--pending`) calls `_auto_mark_done()` first. It maps each document to a notes file, either `notes_{doc_id}.md` or a batch notes file whose header lists it in `doc_ids`, and marks it `processed=True` with a root-relative `batch_notes_file`. There is no `--mark-done`.

**Archive is profile-aware and never touches overrides.** `archive.py` resolves a profile via `skill.py`'s `load_profile` (default `default_profile`) and copies that profile's `output` skill (saved as `SKILL_<profile>.md`) and its corpus's `batch_notes/`, `prompts/`, and `corpus_state.yaml` into the corpus's `archive/`. Reset is scoped to the profile's `refined_into_skill_<profile>` flags (it reuses `is_refined`/`set_refined`). It never reads, copies, or modifies `overrides.yaml`. Overrides persist across all reset modes.

**Conflict detection stops the apply.** If Claude's response contains `## CONFLICT REVIEW`, `skill.py --apply` prints the conflict and exits without writing the profile's `SKILL.md` or updating state. Conflict detection is skipped for `--revision` responses.

**The profile's output path is the target.** `skill.py --apply` writes to the resolved profile's `output` path (creating parent directories as needed). There is no `SKILL_FILE` argument — the path comes from `profiles.yaml`, defaulting to `skills/paper/SKILL.md`.

**Paths resolve from script location.** All scripts use `Path(__file__).parent` as the base so they work when invoked from any directory.

---

## Claude Code skills

The model-driven stages run as project skills in `.claude/skills/` (tracked; the `.gitignore` allows `.claude/skills/**` while keeping `settings.local.json` local). They drive the deterministic CLI scripts; the model work happens in cold subagents so a loaded voice skill cannot contaminate the read. **No step ever requires pasting into claude.ai** (author's standing rule). See `DESIGN.md`.

- **`/extract-voice-notes`** (was `/extract-corpus`) — extraction. Reads `corpus.py --info`, resolves targets (`--pending`), strips via `extract.py`, sanity-checks strips (flag-only), then per the corpus's `extraction_mode` spawns **one cold Opus subagent per document** (`per_document`) or **one over the whole pending set** (`batch`, for short documents), and syncs state.
- **`/synthesize-voice`** (was `/build-skill`) — bootstrap, refine, or **revise** (the user's plain-language instructions go through `skill.py --revision`). One cold Opus subagent writes the whole SKILL.md, then `skill.py --apply` (refine halts on `## CONFLICT REVIEW`).
- **`/validate-voice`** — blind test on held-out documents: facts-only brief, drafts with and without the skill, randomized side-by-side for the author, verdicts logged in the corpus's `validation/`.

**Provenance is automatic.** Each notes file's YAML header (`extracted`, `model`) is the source of truth; `corpus.py`'s `_auto_mark_done()` reads it back into `corpus_state.yaml` (`extraction_model`, `extracted_date`) on every status call and shows `[model, date]` in the PROCESSED listing. Headerless legacy notes show `unknown`.

**Fine-tuning layer is prioritized (not yet built).** A draft → critique-against-failure-modes → revise loop will sit between synthesis and apply and take over override injection, replacing the current static `## Manual Overrides` section in `skill.py --apply`. This is the author's chosen next-major-build (after the 14-doc paper-only baseline) because it addresses the observed problem (qualitative evaluation difficulty) rather than speculative defense (genre artifacts). The failure-mode rubric that feeds the critique step will be seeded from logged A/B test failures. Until built, override injection stays inside `skill.py --apply`.

## Current script inventory

| Script / skill | Status |
|--------|--------|
| `paths.py` | New (2026-11) — corpus resolution, local config merge |
| `corpus.py` | Corpus-aware; .docx; holdouts; batch notes; `--info` |
| `extract.py` | Corpus-aware strip-only; .docx |
| `skill.py` | Corpus-aware; batch notes embedded once; `writer_name`, `format_policy` |
| `overrides.py` | Per corpus |
| `archive.py` | Per corpus |
| `/extract-voice-notes` | Project skill; per_document and batch modes |
| `/synthesize-voice` | Project skill; bootstrap / refine / revise |
| `/validate-voice` | Project skill; new, untested on a real corpus |

## Session handoff

**Completed this session (2026-06-24, "build + validate the 14-doc baseline"):**
- Collected the full paper corpus: registered 8 new PDFs (7 journal papers + 1 proposal) from `~/Desktop/projects/my_corpus/`, reaching 19 total docs / 14 paper-profile docs (12 journal_paper + 2 proposal).
- Extracted all 9 pending paper docs on **Opus** (`claude-opus-4-8`) one-at-a-time via the `/extract-corpus` steps, with provenance headers.
- **Re-extracted the 5 prior sonnet paper docs on Opus** for a model-uniform baseline (their `refined_into_skill_paper` flags persisted from the old build — harmless for a bootstrap rebuild). `corpus.py` re-reads notes headers on every status call, so provenance updated to opus automatically.
- Archived the sonnet-built skill (`archive/run_2026-06-24_*_paper_sonnet_baseline/`, no reset), then **rebuilt `skills/paper/SKILL.md` from all 14 Opus notes** via `/build-skill paper`. Result: 6 full HIGH dimensions (vs 4 in the sonnet build), ~2,300 tokens, failure-mode guardrails baked in.
- **Deployed two ways:** (1) full skill into the Overleaf repo at `~/Desktop/projects/volcanos/ExoVolcano_ExoCAM_Part1/.claude/skills/paper-voice/SKILL.md` (Overleaf-coupled); (2) a register-only, uploadable claude.ai copy at `skills/paper/paper-voice_browser.md` (frontmatter kept, Overleaf wording removed). *(Superseded 2026-09-23 by commit 2524493: these two copies competed, so one skill now covers both surfaces. It is installed by skill-sync from `skills/paper/SKILL.md`.)*
- Added a `*_browser.md` `.gitignore` rule (commit 78f8912) so derived browser copies are untracked like `SKILL.md`.
- **Author-validated across 3 browser A/B tests** (paper rewrite, proposal opening, long multi-paragraph passage). Voice transfers faithfully and holds calibration at length. Author judged it "good enough for my Overleaf workflow" (Claude takes a first cut at some descriptive prose; author always reads/cleans).

**2026-11-16: multi-corpus refactor (branch `multi-corpus`).** Reopened the repo for a second author (association GR writing; local-only, see `profiles.local.yaml`). Moved Eric's data into `corpora/wolf/`, made every script corpus-aware via `paths.py`, added .docx ingestion, batch extraction, holdouts, `/validate-voice`, revise mode, and an advocacy rubric and templates. Regression check: the paper bootstrap prompt is byte-identical before and after (only the timestamp differs). Also fixed two latent bugs: 9 paper notes paths pointed at an old `/Users/wolfe/...` location (a paper rebuild on this machine would have silently used only 5 notes), and the refine prompt counted new documents as already incorporated. The second author's 14 columns are NOT yet registered or extracted; the author decides when. Before the first extraction: set `writer_name` in `profiles.local.yaml` and choose 2 holdout columns.

**Status 2026-10-18: maintenance mode.** The skill does its job and the author judged further work not worth the token cost. Steps 2 and 3 below are on hold indefinitely and public sharing is dropped. Touch the repo only to rebuild after adding a paper, or on a specific request.

**Next work (author's chosen sequence — step 1 & 2 now DONE):**
1. ~~Build the full 14-doc paper-only baseline~~ — DONE; deployed and validated.
2. Write the explicit **failure-mode rubric**, now seeded with real test evidence (see `memory/failure-mode-rubric-seeds.md`): em-dash override enforces only ~2-of-3; full author punctuation register = no em-dash / colon / semicolon; register-scope under-reading (self-corrected); plus the pre-existing seeds (genericity, adverb overuse, "Note that" openers, drifted terminology).
3. Build the draft→critique→revise fine-tuning loop against that rubric, with a **deterministic punctuation post-check (regex)** as the obvious first win — it replaces the leaky prompt-injected override mechanism. Author first deferred adding colons/semicolons to `overrides.yaml` for this reason, then reversed that on 2026-10-18 and added `ov002` (limit colons/semicolons, never use them to replace an em dash) as an interim fix. The loop is on hold.

**Open threads:**
- Still no tooling for deploying the built skill into the Overleaf repo — manual `cp` was used this session.
- Fine-tuning layer remains designed-but-unbuilt; it is now the clear next build (steps 2–3 above).
- `skills/paper/SKILL.md` was hand-rewritten 2026-10-18 without colons, semicolons, or em dashes (commit f034bbd). `core/SKILL_TEMPLATE_PAPER.md` and `templates/synthesis_paper.md` were NOT updated, so a `/build-skill` rebuild will reintroduce that punctuation. Clean those first before rebuilding. Author deferred this as not worth the token cost for now.
