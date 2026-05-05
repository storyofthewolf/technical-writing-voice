#!/usr/bin/env python

"""
skill.py
--------
Builds and maintains SKILL.md from corpus batch notes.

Usage:
    python skill.py --bootstrap
        First-time synthesis prompt from all processed notes.
        Paste output into Claude → save response as SKILL.md.

    python skill.py --refine FILE
        Refinement prompt comparing a specific notes file against current SKILL.md.
        Paste output into Claude → save response → run --apply.

    python skill.py --refine --all
        Refinement prompt bundling all unrefined notes against current SKILL.md.

    python skill.py --apply CLAUDE_RESPONSE
        Apply Claude's refinement response to SKILL.md (conflict-checks first).
        Backs up current SKILL.md to skills/SKILL_{timestamp}.md before writing.

    python skill.py --overrides
        Append or replace the ## Manual Overrides section in SKILL.md from overrides.yaml.

    python skill.py --output FILE
        Write prompt to FILE instead of the default prompts/ path.

Dependencies:
    pip install pyyaml
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).parent

OVERRIDES_FILE = HERE / "overrides.yaml"
STATE_FILE = HERE / "corpus_state.yaml"
SKILL_FILE = HERE / "SKILL.md"
SKILL_TEMPLATE_FILE = HERE / "core" / "SKILL_TEMPLATE.md"
REFINEMENT_PROMPT_FILE = HERE / "templates" / "refinement_prompt.md"
REVISION_PROMPT_FILE = HERE / "templates" / "revision_prompt.md"
SYNTHESIS_PROMPT_FILE = HERE / "templates" / "synthesis_prompt.md"
EVALUATION_DIMENSIONS_FILE = HERE / "core" / "EVALUATION_DIMENSIONS.md"


# ---------------------------------------------------------------------------
# Overrides
# ---------------------------------------------------------------------------

def load_overrides() -> list:
    if not OVERRIDES_FILE.exists():
        return []
    with open(OVERRIDES_FILE) as f:
        data = yaml.safe_load(f) or []
    return data if isinstance(data, list) else []


def _overrides_block(overrides: list) -> str:
    if not overrides:
        return ""
    lines = ["## Manual Overrides", ""]
    for i, o in enumerate(overrides, 1):
        lines.append(f"{i}. {o['instruction']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if not STATE_FILE.exists():
        print("ERROR: corpus_state.yaml not found. Run corpus.py --add first.")
        sys.exit(1)
    with open(STATE_FILE) as f:
        return yaml.safe_load(f) or {"documents": []}


def load_file(path: Path, label: str) -> str:
    if not path.exists():
        print(f"ERROR: {label} not found at {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Corpus weight calculation
# ---------------------------------------------------------------------------

def compute_corpus_stats(state: dict) -> dict:
    processed = [d for d in state["documents"] if d.get("processed")]
    raw_tokens = sum(d.get("prose_tokens", 0) for d in processed)
    effective_tokens = sum(
        d.get("prose_tokens", 0) * d.get("confidence", 3) / 5.0
        for d in processed
    )
    return {
        "doc_count": len(processed),
        "raw_tokens": raw_tokens,
        "effective_tokens": effective_tokens,
        "processed_docs": processed,
    }


def compute_new_doc_influence(new_doc: dict, corpus_stats: dict) -> float:
    new_effective = new_doc.get("prose_tokens", 0) * new_doc.get("confidence", 3) / 5.0
    corpus_effective = corpus_stats["effective_tokens"]
    if corpus_effective + new_effective == 0:
        return 1.0
    return new_effective / (corpus_effective + new_effective)


# ---------------------------------------------------------------------------
# Collect unrefined notes
# ---------------------------------------------------------------------------

def get_unrefined_notes(state: dict) -> list[dict]:
    return [
        d for d in state["documents"]
        if d.get("processed") and not d.get("refined_into_skill")
    ]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def build_bootstrap_prompt(state: dict) -> str:
    synthesis_prompt = load_file(SYNTHESIS_PROMPT_FILE, "synthesis_prompt.md")
    skill_template = load_file(SKILL_TEMPLATE_FILE, "SKILL_TEMPLATE.md")
    eval_dims = load_file(EVALUATION_DIMENSIONS_FILE, "EVALUATION_DIMENSIONS.md")
    corpus_stats = compute_corpus_stats(state)

    notes_block = ""
    for doc in corpus_stats["processed_docs"]:
        notes_file = doc.get("batch_notes_file")
        if notes_file and Path(notes_file).exists():
            notes_content = Path(notes_file).read_text(encoding="utf-8")
            notes_block += f"\n\n---\n## Batch notes: {doc['id']}\n\n{notes_content}"
        else:
            notes_block += f"\n\n---\n## Batch notes: {doc['id']}\n[Notes file not found: {notes_file}]"

    metadata_block = f"""## Corpus metadata (for SKILL.md header)

- Documents processed: {corpus_stats['doc_count']}
- Raw prose tokens: {corpus_stats['raw_tokens']:,}
- Effective tokens (confidence-weighted): {corpus_stats['effective_tokens']:,.0f}
- Analysis date: {datetime.now().strftime("%Y-%m")}
"""

    return f"""---
action: bootstrap
output_file: SKILL.md
generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

{metadata_block}

---

## Batch notes (all processed documents)
{notes_block}

---

## EVALUATION_DIMENSIONS.md (reference)

{eval_dims}

---

## SKILL_TEMPLATE.md (output format)

{skill_template}

---

## Synthesis instructions

{synthesis_prompt}
"""


def build_refinement_prompt(new_notes_docs: list[dict], state: dict) -> str:
    refinement_prompt_template = load_file(REFINEMENT_PROMPT_FILE, "refinement_prompt.md")
    current_skill = load_file(SKILL_FILE, "SKILL.md")
    corpus_stats = compute_corpus_stats(state)

    new_notes_block = ""
    influence_notes = []

    for doc in new_notes_docs:
        notes_file = doc.get("batch_notes_file")
        if notes_file and Path(notes_file).exists():
            notes_content = Path(notes_file).read_text(encoding="utf-8")
        else:
            notes_content = f"[Notes file not found: {notes_file}]"

        influence = compute_new_doc_influence(doc, corpus_stats)
        influence_pct = influence * 100

        new_notes_block += f"""
---
## New batch notes: {doc['id']}
**Document type:** {doc['type']}
**Confidence:** {doc['confidence']}/5
**Prose tokens:** {doc.get('prose_tokens', 0):,}
**Influence weight:** {influence_pct:.1f}% of combined corpus
**Interpretation:** This document represents {influence_pct:.1f}% of the total
confidence-weighted evidence. Treat contradictions with the existing SKILL.md
with proportional skepticism — a single document at {influence_pct:.1f}% weight
should not overturn patterns established across the prior corpus without strong
justification.

{notes_content}
"""
        influence_notes.append(f"  {doc['id']}: {influence_pct:.1f}% influence")

    corpus_summary = f"""## Corpus context

Prior corpus effective tokens: {corpus_stats['effective_tokens']:,.0f}
Prior documents processed: {corpus_stats['doc_count']}
New document(s) influence weights:
{chr(10).join(influence_notes)}
"""

    return f"""---
action: refine
output_file: SKILL.md
generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

{corpus_summary}

---

## Current SKILL.md

{current_skill}

---

## New batch notes
{new_notes_block}

---

## Refinement instructions

{refinement_prompt_template}
"""


def build_revision_prompt(instructions: str) -> str:
    revision_prompt_template = load_file(REVISION_PROMPT_FILE, "revision_prompt.md")
    current_skill = load_file(SKILL_FILE, "SKILL.md")

    return f"""---
action: revision
output_file: SKILL.md
generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

## Revision instructions

{instructions}

---

## Current SKILL.md

{current_skill}

---

## Revision guidelines

{revision_prompt_template}
"""


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

CONFLICT_MARKER = "## CONFLICT REVIEW"


def detect_conflict(response_text: str) -> bool:
    return CONFLICT_MARKER in response_text


def print_conflict(response_text: str) -> None:
    idx = response_text.find(CONFLICT_MARKER)
    print("\n" + "=" * 68)
    print("CONFLICT DETECTED — Review required before SKILL.md is updated")
    print("=" * 68)
    print(response_text[idx:])
    print("=" * 68)
    print("\nTo resolve:")
    print("  1. Review the conflict above")
    print("  2. Edit the batch notes or SKILL.md as appropriate")
    print("  3. Rerun: python skill.py --apply <claude_response>")
    print("     with a revised Claude response that resolves the conflict")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_apply(response_file: str, state: dict) -> None:
    response_path = Path(response_file)
    if not response_path.exists():
        print(f"ERROR: Response file not found: {response_path}")
        sys.exit(1)

    response_text = response_path.read_text(encoding="utf-8")

    if detect_conflict(response_text):
        print_conflict(response_text)
        print("\nSKILL.md was NOT updated. Resolve the conflict first.")
        return

    # Inject overrides
    overrides = load_overrides()
    overrides_block = _overrides_block(overrides)
    marker = "## Manual Overrides"
    if marker in response_text:
        response_text = re.sub(
            r"## Manual Overrides\b.*",
            overrides_block,
            response_text,
            count=1,
            flags=re.DOTALL,
        )
    elif overrides_block:
        response_text = response_text.rstrip("\n") + "\n\n---\n\n" + overrides_block + "\n"

    SKILL_FILE.write_text(response_text, encoding="utf-8")
    print(f"SKILL.md updated.")

    # Mark unrefined docs as refined
    updated = 0
    for doc in state["documents"]:
        if doc.get("processed") and not doc.get("refined_into_skill"):
            doc["refined_into_skill"] = True
            doc["refined_date"] = datetime.now().strftime("%Y-%m-%d")
            updated += 1

    if updated:
        from corpus import save_state
        save_state(state)
        print(f"Marked {updated} document(s) as incorporated into SKILL.md.")


def cmd_overrides() -> None:
    if not SKILL_FILE.exists():
        print(f"ERROR: SKILL.md not found at {SKILL_FILE}")
        sys.exit(1)

    overrides = load_overrides()
    if not overrides:
        print("No overrides found in overrides.yaml — nothing to do.")
        return

    overrides_block = _overrides_block(overrides)
    skill_text = SKILL_FILE.read_text(encoding="utf-8")

    marker = "## Manual Overrides"
    if marker in skill_text:
        skill_text = re.sub(
            r"## Manual Overrides\b.*",
            overrides_block,
            skill_text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        skill_text = skill_text.rstrip("\n") + "\n\n---\n\n" + overrides_block + "\n"

    SKILL_FILE.write_text(skill_text, encoding="utf-8")
    print(f"SKILL.md updated with {len(overrides)} override(s).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build and maintain SKILL.md from corpus batch notes."
    )
    parser.add_argument("--bootstrap", action="store_true",
                        help="Generate first-time synthesis prompt from all processed notes")
    parser.add_argument("--refine", metavar="FILE", nargs="?", const="--all",
                        help="Generate refinement prompt for FILE, or --all for all unrefined notes")
    parser.add_argument("--all", action="store_true",
                        help="Used with --refine: bundle all unrefined notes into one prompt")
    parser.add_argument("--revision", metavar="FILE",
                        help="Generate revision prompt from freeform instructions file")
    parser.add_argument("--apply", metavar="CLAUDE_RESPONSE",
                        help="Apply Claude's refinement response to SKILL.md (backs up first)")
    parser.add_argument("--overrides", action="store_true",
                        help="Append or replace ## Manual Overrides section in SKILL.md")
    parser.add_argument("--output", metavar="FILE",
                        help="Write prompt to FILE instead of default prompts/ path")
    args = parser.parse_args()

    if args.overrides:
        cmd_overrides()
        return

    state = load_state()

    if args.apply:
        cmd_apply(args.apply, state)
        return

    datestamp = datetime.now().strftime("%Y-%m-%d")
    new_docs = []

    if args.bootstrap:
        prompt = build_bootstrap_prompt(state)

    elif args.revision:
        revision_path = Path(args.revision)
        if not revision_path.exists():
            print(f"ERROR: Instructions file not found: {revision_path}")
            sys.exit(1)
        if not SKILL_FILE.exists():
            print("No SKILL.md found. Run --bootstrap first.")
            sys.exit(1)
        instructions = revision_path.read_text(encoding="utf-8")
        prompt = build_revision_prompt(instructions)

    elif args.refine is not None:
        if args.all or args.refine == "--all":
            # Bundle all unrefined notes
            unrefined = get_unrefined_notes(state)
            if not unrefined:
                print("No unrefined batch notes found.")
                print("All processed documents have been incorporated into SKILL.md.")
                print("To add new documents: python corpus.py --add <path>")
                return
            if not SKILL_FILE.exists():
                print("No SKILL.md found. Run --bootstrap for first-time synthesis.")
                return
            new_docs = unrefined
            prompt = build_refinement_prompt(unrefined, state)
        else:
            # Specific notes file
            notes_file = args.refine
            matching = [
                d for d in state["documents"]
                if d.get("batch_notes_file") == notes_file or
                   d.get("batch_notes_file") == str(Path(notes_file))
            ]
            if not matching:
                print(f"ERROR: No document found with notes file: {notes_file}")
                print("Make sure you ran: python extract.py --mark-done DOC_ID NOTES_FILE")
                sys.exit(1)
            new_docs = matching
            prompt = build_refinement_prompt(matching, state)

    else:
        parser.print_help()
        return

    PROMPTS_DIR = HERE / "prompts"
    PROMPTS_DIR.mkdir(exist_ok=True)

    if args.output:
        out_path = Path(args.output)
    elif args.bootstrap:
        out_path = PROMPTS_DIR / f"bootstrap_prompt_{datestamp}.md"
    elif args.revision:
        out_path = PROMPTS_DIR / f"revision_prompt_{datestamp}.md"
    else:
        doc_slug = "+".join(d["id"] for d in new_docs)
        out_path = PROMPTS_DIR / f"refinement_prompt_{doc_slug}_{datestamp}.md"

    out_path.write_text(prompt, encoding="utf-8")
    print(f"Prompt written to: {out_path}")
    print(f"Upload {out_path.name} to Claude → save response → run: python skill.py --apply <response_file>")


if __name__ == "__main__":
    main()
