# technical-writing-voice

A pipeline that extracts a writer's voice from a corpus of their own documents and encodes it as **purpose-specific `SKILL.md` files**, one per writing context. Claude applies the skill when writing on that writer's behalf.

The pipeline handles **more than one author**. Each author's documents live in their own corpus workspace (`corpora/<name>/`), with their own rubric, document types, notes, and overrides. Everything runs inside Claude Code: the model work is done by cold subagents launched from three project commands, and nothing is ever pasted into a browser.

Current uses:

- **`paper`** (corpus `wolf`): Eric Wolf's manuscript voice, built from journal papers and proposals. Loaded by Claude Code in Overleaf/LaTeX repos and by claude.ai for professional correspondence. Its skill is tracked at `skills/paper/SKILL.md` and installed by skill-sync.
- **Local-only profiles** (defined in the gitignored `profiles.local.yaml`): voices for other authors, such as an association government-relations writer. Their corpus, notes, and built skill all stay under `corpora/` and are never committed.

---

## Quick start

```bash
# 0. Environment (once)
uv venv && uv pip install -r requirements.txt

# 1. Register documents in a corpus (.pdf, .docx, .txt; a file or a folder)
.venv/bin/python corpus.py --corpus wolf --add path/to/Paper.pdf --type journal_paper
.venv/bin/python corpus.py --corpus NAME --add path/to/folder/ --type column
.venv/bin/python corpus.py --corpus NAME                 # status

# Optional: hold documents out for a blind test, BEFORE the first extraction
.venv/bin/python corpus.py --corpus NAME --set-holdout DOC_ID on
```

Then in Claude Code:

```
/extract-voice-notes --corpus NAME        # strip + cold Opus read -> batch notes
/synthesize-voice PROFILE                 # bootstrap the skill from all notes
/synthesize-voice PROFILE refine          # later: fold in newly extracted docs
/synthesize-voice PROFILE revise "..."    # apply your own plain-language edits
/validate-voice PROFILE                   # blind test on the held-out documents
```

**Returning after a break?** `python corpus.py --corpus NAME` shows every document's status: extracted or not, by which model, built into which skill, held out or not.

---

## How it works

```
Stage 1  Registration     corpus.py              you, deterministic
Stage 2  Extraction       /extract-voice-notes   extract.py strips text; cold Opus subagent(s)
                                                  write batch notes with a provenance header
Stage 3  Synthesis        /synthesize-voice      skill.py assembles the prompt; ONE cold Opus
                                                  subagent writes the whole SKILL.md; skill.py
                                                  --apply writes it, adds overrides, marks docs
Stage 4  Validation       /validate-voice        facts-only brief from each held-out doc; drafts
                                                  with and without the skill; blind comparison
```

Subagents start cold, so a voice skill loaded in the main conversation cannot contaminate a read. See `DESIGN.md` for the architecture.

**Extraction modes** (set per corpus):

- `per_document`: one subagent per document, one notes file each (`notes_{doc}.md`). Right for long documents such as papers.
- `batch`: one subagent reads the whole pending set and writes one notes file (`notes_batch_{date}.md`) that counts how many documents show each pattern. Right for short documents such as 300-word columns, where a single piece shows too little to establish a habit.

**All documents contribute evenly.** No weighting of any kind. A pattern earns its place by recurring across documents. Token counts are informational only.

---

## Corpora and profiles

`profiles.yaml` (tracked) defines corpora and profiles; `profiles.local.yaml` (gitignored) is merged over it for anything that must stay local.

```yaml
corpora:
  wolf:
    root: corpora/wolf
    doc_types: [journal_paper, proposal, research_statement, ...]
    default_type_for_suffix: {.pdf: journal_paper, .txt: technical_email}
    dimensions: core/EVALUATION_DIMENSIONS.md          # the nine-dimension rubric
    extraction_template: templates/extraction_prompt.md
    extraction_mode: per_document

profiles:
  paper:
    corpus: wolf
    skill_name: paper-voice
    writer_name: ...                  # optional; used in the skill's front matter
    purpose: ...
    corpus_types: [journal_paper, proposal]
    synthesis_template: templates/synthesis_paper.md
    skill_template: core/SKILL_TEMPLATE_PAPER.md
    output: skills/paper/SKILL.md     # under corpora/ for a local-only skill
    target_tokens: 3000
    latex_policy: defer               # or format_policy: "<text>" for non-LaTeX writing
```

Each corpus workspace holds:

```
corpora/<name>/
  corpus_state.yaml   documents and their state
  overrides.yaml      manual overrides for this corpus's skills
  batch_notes/        extraction notes
  stripped_text/      plain text of each document
  prompts/            assembled prompts
  archive/            archive.py snapshots
  validation/         briefs, drafts, blind comparisons, verdicts
  skill/              built local-only skills (if the profile's output points here)
```

### Domains

The nine dimensions hold across domains; what to look for under each differs. Each corpus names its rubric file:

| Rubric | Domain | Extraction | Synthesis | Skill template |
|---|---|---|---|---|
| `core/EVALUATION_DIMENSIONS.md` | Scientific papers, proposals, statements | `templates/extraction_prompt.md` | `templates/synthesis_paper.md` | `core/SKILL_TEMPLATE_PAPER.md` |
| `core/domains/EVALUATION_DIMENSIONS_ADVOCACY.md` | Association / government-relations writing to members | `templates/extraction_batch.md` | `templates/synthesis_advocacy.md` | `core/SKILL_TEMPLATE_ADVOCACY.md` |

`templates/extraction_batch.md` is domain-neutral (it takes dimension names from the rubric), so any short-document corpus can use it.

### Adding a new author

1. Pick or write a rubric (copy the closest file in `core/domains/` and rewrite the what-to-look-for questions).
2. Add a corpus and a profile to `profiles.local.yaml` (local) or `profiles.yaml` (tracked). Point a local-only profile's `output` under `corpora/<name>/`.
3. Register, set holdouts, then `/extract-voice-notes`, `/synthesize-voice`, `/validate-voice`.

---

## The nine dimensions

| # | Science rubric | Advocacy rubric |
|---|---|---|
| D1 | Syntactic style | Syntactic style |
| D2 | Semantic style | Semantic style (how policy is made concrete) |
| D3 | Vocabulary | Vocabulary |
| D4 | Rhythm and cadence | Rhythm and cadence |
| D5 | Epistemic stance | Stance and certainty |
| D6 | Argumentation structure | Argumentation structure (news to meaning to action) |
| D7 | Transition logic | Transition logic |
| D8 | Quantitative and figure integration | Numbers and specifics |
| D9 | Register modulation | Register modulation |

---

## Overrides, archiving, and resets

**Overrides** are short editorial directives appended verbatim to a corpus's built skills at apply time. They are never sent to a subagent and survive every reset.

```bash
python overrides.py --corpus wolf list
python overrides.py --corpus wolf add --category punctuation "..."
python overrides.py --corpus wolf remove ov001
python skill.py --profile paper --overrides        # re-inject without a rebuild
```

Use `/synthesize-voice PROFILE revise "..."` for anything that needs nuance.

**Archiving** snapshots one profile's skill plus its corpus's notes, prompts, and state into `corpora/<corpus>/archive/`:

```bash
python archive.py --profile paper --label before_new_docs
python archive.py --profile paper --reset soft     # delete the skill, clear its refined flags, keep notes
python archive.py --profile paper --reset full     # also delete the corpus's batch notes
```

---

## Script reference

All scripts take `--corpus NAME` or `--profile NAME` (default: the default profile's corpus) and resolve paths from their own location.

```
corpus.py   [sel]                              status; auto-marks docs covered by a notes file
corpus.py   [sel] --add PATH ... [--type T] [--notes TEXT]
corpus.py   [sel] --set-type DOC_ID TYPE | --set-notes DOC_ID TEXT
corpus.py   [sel] --set-holdout DOC_ID on|off
corpus.py   [sel] --pending [--pending-types T ...]
corpus.py   [sel] --info                       resolved corpus settings (used by the commands)

extract.py  [sel] DOC_ID ... | --all [--force] strip to corpora/<name>/stripped_text/

skill.py    [--profile P] --bootstrap | --refine [FILE|--all] | --revision FILE  [--output FILE]
skill.py    [--profile P] --apply RESPONSE     write the skill (halts on ## CONFLICT REVIEW)
skill.py    [--profile P] --overrides

overrides.py [sel] list | add [--category C] TEXT | remove ID
archive.py   [--profile P] [--label TEXT] [--reset soft|full]
```

---

## Troubleshooting

**Stripped text looks noisy.** The PDF cleaner is heuristic. `/extract-voice-notes` checks every strip and stops on a corrupted one. Inspect `corpora/<name>/stripped_text/DOC.txt` and re-strip with `extract.py --force`.

**A document was not auto-marked.** Notes are matched by file name (`notes_{doc}.md`) or by the `doc_ids` list in a batch notes header. Run `python corpus.py --corpus NAME` to resync.

**Overrides missing from the skill.** Run `python skill.py --profile P --overrides`.

**Conflict review on refine.** `--apply` writes nothing and shows the conflict. Decide whether it is a real contradiction or genre variation, then rerun `/synthesize-voice P refine` or rebuild with `bootstrap`.
