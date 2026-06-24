# DEVELOPER_NOTES.md

Implementation reference for `technical-writing-voice`. Granular detail for human
code review — too internal for README.md, too detailed for CLAUDE.md.
See `DESIGN.md` for architecture rationale and `CLAUDE.md` for design invariants.

---

## CLI reference

All flags below are verified against each script's argparse.

### corpus.py — registration, status, provenance
```
python corpus.py                                   # status report (auto-marks + syncs provenance)
python corpus.py --add PATH [PATH ...]             # register file(s) or directory(ies)
python corpus.py --add FILE --type TYPE --notes T  # register with metadata
python corpus.py --set-type DOC_ID TYPE            # update document type
python corpus.py --set-notes DOC_ID TEXT           # update notes
python corpus.py --pending                         # print IDs needing extraction (one per line)
python corpus.py --pending --pending-types T [T..] # restrict --pending to document types
```
No `--confidence` / `--set-confidence` — confidence weighting was removed; documents contribute evenly.

### extract.py — strip to text, generate extraction prompt
```
python extract.py DOC_ID [DOC_ID ...]              # strip + build prompt for specific docs
python extract.py --all                            # all unprocessed
python extract.py --mark-done DOC_ID NOTES_FILE    # manual fallback if auto-detect misses a file
```
No `--priority` — it selected the highest-confidence doc; removed with confidence.

### skill.py — build/maintain a profile's SKILL.md
```
python skill.py [--profile NAME] --bootstrap                  # synthesis prompt from profile notes
python skill.py [--profile NAME] --refine NOTES_FILE          # refinement prompt for one notes file
python skill.py [--profile NAME] --refine --all              # refinement prompt, all unrefined notes
python skill.py [--profile NAME] --revision INSTRUCTIONS_FILE # freeform revision prompt
python skill.py [--profile NAME] --apply CLAUDE_RESPONSE      # write response to profile's SKILL.md
python skill.py [--profile NAME] --overrides                  # inject overrides.yaml into the SKILL.md
python skill.py --output FILE                                 # write prompt to FILE instead of prompts/
```
`--profile` defaults to `profiles.yaml` `default_profile` (`paper`).

### overrides.py — manual editorial directives
```
python overrides.py list
python overrides.py add "instruction text" [--category CATEGORY]
python overrides.py remove OVERRIDE_ID
```

### archive.py — snapshot / reset
```
python archive.py [--label TEXT]                   # snapshot only
python archive.py --reset soft                     # snapshot + delete SKILL.md + reset refined flags
python archive.py --reset full                     # snapshot + wipe SKILL.md and batch_notes
```
Never touches `overrides.yaml`.

---

## Claude Code skills (`.claude/skills/`)

| Skill | Drives | Model work |
|-------|--------|-----------|
| `/extract-corpus` | `corpus.py --pending`, `extract.py` | one cold Opus subagent **per document** |
| `/build-skill` | `skill.py --bootstrap`/`--refine --all`/`--apply` | one cold Opus subagent over **all** profile notes |

Both delegate the model read to cold subagents (no inherited skills/context) to
prevent an existing voice skill from contaminating the read. Extraction shards
(per-doc isolation); synthesis cannot shard (must resolve cross-document
conflicts in one context).

---

## Key functions

### corpus.py
- `_parse_notes_header(path) -> dict` — read YAML front matter from a notes file; `{}` if absent/malformed (never raises).
- `_auto_mark_done(state)` — on every status call: marks docs processed when `batch_notes/notes_{id}.md` appears, AND syncs `extraction_model`/`extracted_date` from the notes header (runs for already-processed docs too, so re-extraction with a new model updates the record).
- `cmd_pending(state, types=None)` — print pending doc IDs, one per line, for the extraction skill.
- `_short_model(model_id)` — abbreviate a model id for display (`claude-opus-4-8` → `opus-4-8`); `None` → `model: unknown`.

### skill.py
- `class Profile` — resolved settings for one profile (skill_name, purpose, corpus_types, target_tokens, latex_policy, output path, synthesis_template, skill_template). `.refined_flag` → `refined_into_skill_<name>`; `.matches_type(doc)`.
- `load_profile(name)` — read `profiles.yaml`; falls back to `_legacy_profile()` (single `SKILL.md`) if the file is absent.
- `is_refined(doc, profile)` / `set_refined(doc, profile, value)` — per-profile incorporation flag (legacy mode uses the original `refined_into_skill`).
- `compute_corpus_stats(state, profile)` — doc count + raw tokens (no weighting); filters to the profile's `corpus_types`.
- `build_bootstrap_prompt` / `build_refinement_prompt` / `build_revision_prompt` — assemble the prompt embedding notes, templates, and a profile-directives block.
- `cmd_apply(response_file, state, profile)` — conflict-check (`## CONFLICT REVIEW` → halt), inject overrides, write `profile.output`, mark matching docs incorporated.
- `detect_conflict` / `print_conflict` — conflict marker is the literal `## CONFLICT REVIEW`.

---

## Data structures

### corpus_state.yaml — per-document entry
```yaml
- id: wolf2025psj
  filepath: ../my_corpus/journal_articles/Wolf2025psj.pdf
  type: journal_paper                  # journal_paper|proposal|research_statement|
                                       # letter_of_rec|review_perspective|technical_email|other
  prose_tokens: 40321                  # informational corpus size; NOT a weight
  processed: true
  batch_notes_file: batch_notes/notes_wolf2025psj.md
  refined_into_skill: true             # legacy flag; profiles use refined_into_skill_<profile>
  added: '2026-04-18'
  notes: ''
  processed_date: '2026-04-23'         # when corpus.py first detected the notes file
  extraction_model: claude-sonnet-4-6  # synced from notes header
  extracted_date: '2026-04-23'         # synced from notes header
```
No `confidence` field on new registrations (removed). Stale `confidence:` keys in
existing entries are inert — nothing reads them.

### notes_{doc}.md — provenance header (source of truth)
```
---
doc_id: wolf2025psj
extracted: 2026-06-23
model: claude-opus-4-8     # full model id; the skill passes the exact id it ran
---
```

### profiles.yaml — one entry per purpose-specific skill
```yaml
default_profile: paper
profiles:
  paper:
    skill_name: eric-wolf-paper-voice
    purpose: >...                       # injected into the synthesis prompt
    corpus_types: [journal_paper, proposal]
    synthesis_template: templates/synthesis_paper.md
    output: skills/paper/SKILL.md
    target_tokens: 3000
    latex_policy: defer                 # do NOT prescribe LaTeX/.bib markup in the skill
```
Adding a profile is a data edit — no script changes.

---

## Conventions / gotchas

- Scripts resolve paths from `Path(__file__).parent` — runnable from any directory.
- Gitignored (local data, not source): `corpus_state.yaml`, `overrides.yaml`, `SKILL.md` (matches `skills/*/SKILL.md` too), `batch_notes/`, `stripped_text/`, `prompts/`, `archive/`.
- `.claude/`: only `settings.local.json` is ignored; `.claude/skills/**` is tracked.
- Confidence weighting fully removed — see the "all documents contribute evenly" invariant in CLAUDE.md.
- `templates/extraction_prompt.md` is the single analysis contract shared by the Claude Code path and any manual claude.ai run.
