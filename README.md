# technical-writing-voice

A pipeline for extracting a scientist's technical writing voice from a corpus of their own documents and encoding it as **purpose-specific `SKILL.md` files** — one per writing context. The result is a set of voice skills Claude applies when writing on the author's behalf.

**Profiles.** The pipeline no longer targets one monolithic skill. `profiles.yaml` defines a separate, narrow skill per writing purpose. The primary profile is **`paper`**: a slim manuscript-writing voice built from journal papers and proposals only, designed for **Claude Code to load when editing a GitHub-backed Overleaf/LaTeX repository**. It governs prose voice and argument structure; LaTeX, `.bib`, and figure markup are left to Claude's standard conventions. Informal registers (emails, letters, statements) are intentionally out of scope — that personal-touch writing resists AI help, whereas formal manuscript prose is where assistance pays off.

`profiles.yaml` is required — it defines the available skills. Where the docs below say "SKILL.md," read it as "the selected profile's `SKILL.md`" (default: `skills/paper/SKILL.md`), and add `--profile NAME` to `skill.py` commands to target a specific profile.

---

## Quick start

The whole pipeline runs inside Claude Code. The two model-driven stages are slash-command skills; you only run `corpus.py` by hand. See `DESIGN.md` for the architecture.

```bash
# 1. Register documents you want in the voice (papers + proposals for the paper profile).
#    No confidence rating — every registered document contributes evenly, so register
#    only what you actually want to represent your voice.
python corpus.py --add path/to/Paper.pdf --type journal_paper --notes "sole author"
python corpus.py --add path/to/proposals/        # a whole directory at once
python corpus.py                                 # status check
```

```
2. Extract — in Claude Code, just invoke the skill:
   /extract-corpus                  # all pending docs (one cold Opus subagent each)
   /extract-corpus wolf_2018        # or specific doc IDs
   → writes batch_notes/notes_{doc}.md with a model+date provenance header

3. Build the skill — also a Claude Code skill:
   /build-skill                     # bootstrap the paper profile from all its notes
   /build-skill --refine            # later: fold in newly added docs (halts on conflict)
   → writes skills/paper/SKILL.md (overrides injected, docs marked incorporated)
```

```bash
# 4. Deploy: copy the built skill into the repo where you actually write,
#    so Claude Code loads it when you edit LaTeX.
cp skills/paper/SKILL.md /path/to/overleaf-repo/.claude/skills/paper-voice/SKILL.md
```

**Returning after a break?** Run `python corpus.py` — it shows every document's status (extracted? which model? incorporated into the skill?). To add a manual editorial directive that survives every rebuild: `python overrides.py add "..."`.

---

## What this project does

Most AI writing assistance produces generic academic prose. This pipeline produces something different: a structured voice model built by machine-analyzing the author's own documents across nine linguistic dimensions — syntax, semantics, vocabulary, rhythm, epistemic stance, argumentation, transitions, quantitative integration, and register modulation. The result is a `SKILL.md` file that Claude reads as a persistent Project instruction, allowing it to write in a voice a colleague would recognize.

The pipeline is **additive**. You start with a small bootstrap corpus and refine the voice model incrementally as you add documents. New documents are compared against the existing `SKILL.md` rather than reprocessing everything from scratch. When a new document contradicts an established pattern, the pipeline stops and asks for your input rather than silently overwriting.

**Manual overrides** let you inject editorial directives directly into the final `SKILL.md` — instructions that survive every refinement run and are never touched by the LLM.

**Archiving** lets you snapshot and reset the pipeline at any point, enabling comparison across prompt versions or LLMs without losing prior work.

---

## Quick orientation (read this when returning after a break)

The pipeline has three stages. Each stage produces an output that feeds the next. Stages 2 and 3 run as Claude Code skills (cold Opus subagents do the model work); only Stage 1 is run by hand.

```
Stage 1 — Registration                          (you, deterministic)
  corpus.py           Register PDF/TXT documents; set type, notes

Stage 2 — Extraction                            (/extract-corpus skill)
  extract.py          Strip document to plain text  (driven by the skill)
  cold Opus subagent  Read text → write batch_notes/notes_{doc}.md + provenance header
  corpus.py           Auto-syncs status and provenance on next check

Stage 3 — Skill building                        (/build-skill skill)
  skill.py            Assemble bootstrap/refinement prompt  (driven by the skill)
  cold Opus subagent  Synthesize the complete SKILL.md from all the notes
  skill.py --apply    Write skills/<profile>/SKILL.md; inject overrides; halt on conflict
```

The older claude.ai copy-paste flow is gone; the `skill.py`/`extract.py` CLI commands still exist and are what the skills call under the hood (and remain usable directly if you prefer).

**To check where you left off:**
```bash
python corpus.py
```
This prints the status of every registered document — which are extracted, which model produced the notes, and which have been incorporated into the skill.

---

## Repository structure

```
technical-writing-voice/
│
├── README.md                            ← this file
│
├── corpus.py                            ← register and manage documents
├── extract.py                           ← strip PDFs to text; generate extraction prompts
├── skill.py                             ← generate prompts for SKILL.md; apply responses
├── overrides.py                         ← manage manual override instructions
├── archive.py                           ← snapshot and reset the pipeline
│
├── core/                                ← stable definitions; read once, do not modify
│   ├── PROJECT_INSTRUCTIONS.md          ← add to Claude Project knowledge
│   ├── EVALUATION_DIMENSIONS.md         ← definitions of all nine voice dimensions
│   └── SKILL_TEMPLATE.md                ← output format template for SKILL.md
│
├── templates/                           ← LLM instruction templates; never modified by scripts
│   ├── extraction_prompt.md             ← instructions for voice extraction
│   ├── synthesis_prompt.md              ← instructions for first-time SKILL.md synthesis
│   ├── refinement_prompt.md             ← instructions for refining an existing SKILL.md
│   └── revision_prompt.md               ← instructions for applying manual revision directives
│
│ ── not tracked in git ──
├── corpus_state.yaml                    ← auto-generated: tracks all registered documents
├── overrides.yaml                       ← your manual editorial directives; persists across resets
├── SKILL.md                             ← your personal voice model; add to Claude Project knowledge
├── prompts/                             ← generated prompts; upload these to Claude
│   ├── bootstrap_prompt_DATE.md
│   ├── refinement_prompt_DOCID_DATE.md
│   └── revision_prompt_DATE.md
├── batch_notes/                         ← extraction prompts and Claude's notes responses
│   ├── prompt_DOCID.md                  ← upload to Claude
│   └── notes_DOCID.md                   ← download from Claude; save here
├── stripped_text/                       ← cached plain text extracted from PDFs
└── archive/                             ← snapshots from archive.py
    └── run_YYYY-MM-DD_HHMMSS[_label]/
```

---

## Setup

### Dependencies

```bash
pip install pymupdf tiktoken pyyaml
```

### Which Claude model to use

Use **claude-sonnet-4-6** for all sessions. It has sufficient context window for large documents and the pattern recognition the extraction prompt demands. Haiku is too weak for nuanced voice extraction; Opus is unnecessary.

### Claude Project setup

1. Create a dedicated Claude Project for voice extraction (separate from any writing project)
2. Add `core/PROJECT_INSTRUCTIONS.md` to the Project knowledge
3. Add `SKILL.md` to the Project knowledge once it exists — update it there after each `--apply` run

`core/PROJECT_INSTRUCTIONS.md` tells Claude how to handle uploaded prompt files. No additional chat instructions are needed.

---

## Full workflow

### Stage 1 — Register your documents

Register each source document before doing anything else. Registration records the file path, document type, and any notes in `corpus_state.yaml`.

```bash
# Register a single document with metadata
python corpus.py --add pdfs/wolf_2022.pdf \
    --type journal_paper \
    --notes "sole author, high signal"

# Register a whole directory (defaults applied — update metadata afterward)
python corpus.py --add pdfs/

# Update metadata on an already-registered document
python corpus.py --set-type wolf_2022 journal_paper
python corpus.py --set-notes wolf_2022 "sole author, high signal"

# Check current corpus status
python corpus.py
```

**Document types:**
`journal_paper`, `proposal`, `research_statement`, `letter_of_rec`, `review_perspective`, `technical_email`, `other`

**All documents contribute evenly.** There is no confidence rating or weighting — a pattern earns its place by recurring across documents, not by any per-document score. Token counts are recorded only as informational corpus size. Curate the corpus for representativeness rather than relying on weights: note co-authorship or constrained formats in `--notes` so extraction can flag sections that read as another author's voice.

---

### Stage 2 — Extract documents (repeat per document)

Extraction strips a document to plain text and generates a prompt that Claude uses to observe your voice patterns. Each document is extracted independently — Claude does not need context from previous extractions.

**Step 2a — Generate the extraction prompt**

```bash
# Extract a specific document by ID
python extract.py wolf_2022

# Extract all unprocessed documents at once
python extract.py --all
```

This produces two files:
- `stripped_text/wolf_2022.txt` — plain text from the PDF; **inspect this before uploading** to verify quality
- `batch_notes/prompt_wolf_2022.md` — ready-to-upload extraction prompt

**Step 2b — Run extraction in Claude**

1. Open your Claude Project
2. Upload `batch_notes/prompt_wolf_2022.md`
3. Claude returns `notes_wolf_2022.md` as a downloadable artifact
4. Save it to `batch_notes/notes_wolf_2022.md`

**Step 2c — Mark as done**

`corpus.py` detects completed extractions automatically. Just run a status check:

```bash
python corpus.py
```

If `batch_notes/notes_wolf_2022.md` exists, the document is auto-marked as processed. No manual command needed.

If auto-detection does not pick it up (e.g. you saved the file with a different name), mark it manually:

```bash
python extract.py --mark-done wolf_2022 batch_notes/notes_wolf_2022.md
```

Repeat Stage 2 for each document you want in your bootstrap corpus (aim for 5–8 documents).

---

### Stage 3a — Bootstrap SKILL.md (first time only)

Once you have extracted at least 5 documents, generate the bootstrap prompt. This synthesizes all notes into the first version of `SKILL.md`.

**Step 3a-1 — Generate the bootstrap prompt**

```bash
python skill.py --bootstrap
# writes: prompts/bootstrap_prompt_DATE.md
```

**Step 3a-2 — Run synthesis in Claude**

1. Upload `prompts/bootstrap_prompt_DATE.md` to your Claude Project
2. Claude runs the full synthesis and returns `SKILL.md` as a downloadable artifact
3. Save it anywhere temporarily (e.g. `downloads/SKILL_response.md`)

**Step 3a-3 — Apply the response**

```bash
python skill.py --apply downloads/SKILL_response.md
```

This:
- Conflict-checks the response (bootstrap should never trigger a conflict)
- Injects any existing `overrides.yaml` entries as a `## Manual Overrides` section
- Writes the result to `SKILL.md` in the project root
- Marks all processed documents as incorporated in `corpus_state.yaml`

**Step 3a-4 — Add SKILL.md to your Claude Project knowledge**

Upload `SKILL.md` to your Claude Project knowledge base. The voice model is now active.

---

### Stage 3b — Refine SKILL.md (each new document)

When you add a new document to the corpus, refine the existing `SKILL.md` rather than re-bootstrapping. The refinement prompt compares the new notes against the current `SKILL.md` and produces an updated version.

**Step 3b-1 — Register and extract the new document**

Follow Stage 1 and Stage 2 for the new document. Run `python corpus.py` to confirm it is marked processed.

**Step 3b-2 — Generate the refinement prompt**

```bash
# Refine using a specific notes file
python skill.py --refine batch_notes/notes_wolf_2024.md

# Refine using all notes not yet incorporated into SKILL.md
python skill.py --refine --all
# writes: prompts/refinement_prompt_DOCID_DATE.md
```

**Step 3b-3 — Run refinement in Claude**

1. Upload the generated prompt file to your Claude Project
2. Claude compares the new notes against the current `SKILL.md` and returns one of:
   - An updated `SKILL.md` — no conflicts, proceed normally
   - A response containing `## CONFLICT REVIEW` — a contradiction was detected; see below

**Step 3b-4 — Apply the response**

```bash
python skill.py --apply downloads/SKILL_response.md
```

Same as bootstrap apply: conflict check, overrides injection, writes `SKILL.md`, marks docs as incorporated.

**Step 3b-5 — Update SKILL.md in your Claude Project knowledge**

Replace the existing `SKILL.md` in your Project knowledge base with the new version.

**If a conflict is detected:**

`--apply` prints the conflict block and exits without writing `SKILL.md`. The conflict block contains:
- The contradicting evidence from the new notes
- The established pattern in the current `SKILL.md`
- Claude's recommendation

Review it, decide which evidence is more representative, then either:
- Edit the batch notes to clarify the discrepancy, re-upload the refinement prompt, and re-apply
- Accept the conflict as register variation and re-upload the prompt with a note to Claude to treat it as such

---

### Stage 3c — Revise SKILL.md with manual instructions

Use `--revision` when you want to make freeform editorial changes to `SKILL.md` — for example, correcting a pattern that feels wrong, restructuring a section, or adding nuance that the automated analysis missed.

**Step 3c-1 — Write your revision instructions**

Create a plain text or markdown file with your instructions. Be specific — Claude will apply them literally.

Example `my_revisions.md`:
```
The current D4 Rhythm section overstates my use of short sentences. In practice,
I use short sentences primarily at the end of paragraphs to land a point, not
throughout. Revise D4 to reflect this: short sentences are a punctuation device,
not a general habit.

Also, D7 Transition Logic does not mention my use of "this suggests" as a
hedged interpretive pivot. Add this as a noted phrase under that dimension.
```

**Step 3c-2 — Generate the revision prompt**

```bash
python skill.py --revision my_revisions.md
# writes: prompts/revision_prompt_DATE.md
```

**Step 3c-3 — Run revision in Claude**

Upload `prompts/revision_prompt_DATE.md` to your Claude Project. Claude applies your instructions and returns an updated `SKILL.md`.

**Step 3c-4 — Apply the response**

```bash
python skill.py --apply downloads/SKILL_response.md
```

No conflict detection runs for revisions — your instructions are treated as authoritative.

**Step 3c-5 — Update SKILL.md in your Claude Project knowledge**

---

### Managing manual overrides

Manual overrides are single-line editorial directives appended verbatim to every `SKILL.md` produced by `--apply`. They are never seen by Claude during extraction or synthesis — they are post-processing only. They survive all pipeline resets.

```bash
# List current overrides
python overrides.py list

# Add an override
python overrides.py add "Never use em-dashes"
python overrides.py add "Always include inline citations when making factual claims"
python overrides.py add --category style "Prefer active voice in discussion sections"

# Remove an override by ID
python overrides.py remove ov001

# Inject current overrides into SKILL.md without running a full apply
python skill.py --overrides
```

Overrides appear in `SKILL.md` as a `## Manual Overrides` section at the end of the file. Use `--revision` (not overrides) for changes that require nuance or multi-sentence instructions.

---

### Archiving and resetting

Use `archive.py` to snapshot a profile's pipeline state before a reset or a major change. It is profile-aware (`--profile NAME`, default: `default_profile`). Archives capture the profile's built skill (its `output`, e.g. `skills/paper/SKILL.md`, saved as `SKILL_<profile>.md`), plus the shared `batch_notes/`, `prompts/`, and `corpus_state.yaml`. The orphaned root `SKILL.md` and `overrides.yaml` are never archived or reset.

```bash
# Snapshot only (safe checkpoint before any change)
python archive.py

# Snapshot a specific profile with a descriptive label
python archive.py --profile paper --label before_new_docs

# Soft reset: delete the profile's SKILL.md, reset its refined flags, keep batch notes
# Use when: re-synthesizing the skill after editing templates or switching LLMs
python archive.py --reset soft

# Full reset: delete the profile's SKILL.md and all batch notes, reset all state flags
# Use when: starting the entire pipeline from scratch
python archive.py --reset full --label clean_slate
```

Reset is scoped to the selected profile — it touches only that profile's `refined_into_skill_<profile>` flags and its own `output` skill, never another profile's.

**Soft reset** preserves all extraction work. After a soft reset, run `python skill.py --bootstrap` to regenerate the profile's skill from the existing notes.

**Full reset** wipes everything except registered document paths and `overrides.yaml`. After a full reset, re-run Stage 2 (extraction) for all documents before bootstrapping.

Archives are saved to `archive/run_YYYY-MM-DD_HHMMSS_<profile>[_label]/` and are not tracked in git.

---

## The nine voice dimensions

Defined in full in `core/EVALUATION_DIMENSIONS.md`.

| # | Dimension | What it captures |
|---|-----------|-----------------|
| D1 | Syntactic Style | Sentence construction, clause ordering, punctuation as structure |
| D2 | Semantic Style | Abstraction, concreteness, analogy, movement between scales |
| D3 | Vocabulary | Preferred synonyms, hedging language, signature connective phrases |
| D4 | Rhythm and Cadence | Sentence, paragraph, and section-level pacing |
| D5 | Epistemic Stance | Where the writer commits vs. hedges, how certainty is signaled |
| D6 | Argumentation Structure | How cases are built, where evidence and interpretation sit |
| D7 | Transition Logic | The connective tissue between ideas — often the most fingerprint-like |
| D8 | Quantitative Integration | How numbers, equations, and figures are narrated |
| D9 | Register Modulation | How voice shifts across document types — assessed at synthesis only |

---

## Corpus guidance

### Minimum viable bootstrap corpus

- At least 2 journal papers with clear first-author editorial control
- At least 1 proposal narrative (significance or approach section)
- At least 1 research statement or review article
- At least 1 technical email grouping if available

Even a modest email corpus adds disproportionate signal. Technical emails sit at the low-scaffold end of the spectrum and reveal the reasoning style that operates when no genre conventions apply.

### What makes a good corpus

**Sole-authored documents first.** Co-authored documents blend voices. Since all documents contribute evenly, curate rather than weight: include co-authored documents only where you had clear editorial control over specific sections, and note the co-authorship so extraction can flag any sections that read as another author's voice.

**Diversity over volume.** A corpus spanning four document types at 80k tokens is more informative than 400k tokens of journal papers alone. The voice model needs the full register range to assess D9 Register Modulation.

**Recency matters less than you think.** Unless your voice has changed significantly in the last five years, a corpus drawn from any representative span is fine. Voice evolves slowly.

**Curate the corpus deliberately.** With no weighting, the corpus *is* the model: every registered document counts the same, so exclude documents that misrepresent your voice rather than down-rating them.

### Token guidance

PDFs are stripped to plain text before analysis — figures, reference lists, author listings, page numbers, and axis labels are removed. Expect roughly 40–60% token reduction from raw PDF to cleaned prose for a typical paper.

Rough stripped token budgets:
- Journal paper (sole author): 15,000–25,000 tokens
- Proposal (full narrative): 20,000–35,000 tokens
- Research statement: 3,000–8,000 tokens
- Technical email corpus: 5,000–15,000 tokens

---

## Script reference

### corpus.py

```
python corpus.py                                        # status report; auto-marks completed extractions
python corpus.py --add FILE [FILE ...]                  # register one or more documents
python corpus.py --add DIR/                             # register all files in a directory
python corpus.py --add FILE --type TYPE --notes TEXT
python corpus.py --set-type DOC_ID TYPE
python corpus.py --set-notes DOC_ID TEXT
```

### extract.py

```
python extract.py DOC_ID [DOC_ID ...]                   # extract specific documents
python extract.py --all                                 # extract all unprocessed documents
python extract.py --mark-done DOC_ID NOTES_FILE         # manual fallback if auto-detect misses a file
```

### skill.py

`--profile NAME` selects the profile from `profiles.yaml` (default: `paper`). Each action targets that profile's output path and `corpus_types`-filtered notes.

```
python skill.py [--profile NAME] --bootstrap                  # synthesis prompt from the profile's notes
python skill.py [--profile NAME] --refine NOTES_FILE          # refinement prompt for one notes file
python skill.py [--profile NAME] --refine --all              # refinement prompt for the profile's unrefined notes
python skill.py [--profile NAME] --revision INSTRUCTIONS_FILE # revision prompt from freeform instructions
python skill.py [--profile NAME] --apply CLAUDE_RESPONSE      # write Claude's response to the profile's SKILL.md
python skill.py [--profile NAME] --overrides                  # inject overrides.yaml into the profile's SKILL.md
python skill.py --output FILE                                 # write prompt to FILE instead of prompts/
```

### profiles.yaml

Defines each purpose-specific skill. Add an entry to create a new skill; no script changes needed.

```yaml
default_profile: paper
profiles:
  paper:
    skill_name: paper-voice
    purpose: Formal journal-paper and proposal manuscript writing ...
    corpus_types: [journal_paper, proposal]   # which docs feed this skill
    synthesis_template: templates/synthesis_paper.md
    output: skills/paper/SKILL.md
    target_tokens: 3000                        # length budget given to Claude
    latex_policy: defer                        # Claude uses its own LaTeX/.bib conventions
```

### overrides.py

```
python overrides.py list
python overrides.py add "instruction text"
python overrides.py add --category CATEGORY "instruction text"
python overrides.py remove OVERRIDE_ID
```

### archive.py

```
python archive.py [--profile NAME]                     # snapshot only
python archive.py [--profile NAME] --label TEXT         # snapshot with label
python archive.py [--profile NAME] --reset soft         # snapshot + delete profile SKILL.md + reset its refined flags
python archive.py [--profile NAME] --reset full         # snapshot + full wipe of profile SKILL.md and batch_notes
```

---

## Troubleshooting

**Not sure where you left off**
Run `python corpus.py` — it shows which documents are registered, extracted, and incorporated into `SKILL.md`.

**`corpus_state.yaml not found`**
Run `python corpus.py --add <path>` first to register at least one document.

**Document not auto-marked after saving notes file**
The auto-mark check runs when you invoke `python corpus.py`. Make sure the notes file is saved to `batch_notes/` with the exact name `notes_DOCID.md` where `DOCID` matches the document ID in `corpus_state.yaml`.

**Stripped text looks noisy**
Inspect `stripped_text/DOCID.txt` before uploading the extraction prompt. The cleaner is heuristic-based and may miss noise in unusual PDF layouts — watch for multi-column layout interleaving, non-standard figure labels, and unusual reference formats.

**Overrides not appearing in SKILL.md**
Overrides are injected by `skill.py --apply`, not by Claude. If you added overrides after the last `--apply` run, either re-run `--apply` with the same response file or run `python skill.py --overrides` to inject them directly.

**SKILL.md feels too generic**
The most common cause is a corpus dominated by co-authored journal papers. Add a research statement or technical email corpus — these carry the highest voice signal per token and will pull the model toward your actual reasoning style.

**Conflict review triggered unexpectedly**
Check whether the conflict is a genuine contradiction or register variation. Different syntactic habits between an email corpus and a journal paper is expected register variation, not a contradiction. Claude's conflict block explains its reasoning — review it before deciding how to respond.

**Script cannot find templates or core files**
All scripts resolve paths relative to their own location. Run scripts from the project root directory or use their full path: `python /path/to/project/skill.py --bootstrap`.
