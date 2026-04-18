"""
refine.py
---------
Prepares a refinement prompt that compares new batch notes against the current
SKILL.md and produces an updated SKILL.md. Handles three cases:

  1. Confirmation — new document supports existing patterns (auto-updates confidence)
  2. Addition — new document reveals patterns not in current SKILL.md (auto-adds)
  3. Contradiction — new document conflicts with existing patterns (STOPS, asks you)

If Claude's response contains a CONFLICT REVIEW block, refine.py prints it
for your review and does not write to SKILL.md until you resolve it.

Usage:
    # After marking a document done with extract.py:
    python refine.py                          # refine using all unprocessed notes
    python refine.py --notes batch_notes/notes_myDoc.md   # specific notes file
    python refine.py --bootstrap              # first-time: synthesis from all notes

    # After resolving a conflict Claude flagged:
    python refine.py --resolve               # rerun after you've edited the notes

Output:
    Prints a ready-to-paste prompt. Paste into Claude, save response.
    Then run: python refine.py --apply SKILL.md path/to/claude_response.md

Dependencies:
    pip install pyyaml
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# All paths resolve relative to this script's directory so the script
# can be invoked from any working directory.
HERE = Path(__file__).parent

STATE_FILE = HERE / "corpus_state.yaml"
SKILL_FILE = HERE / "SKILL.md"
SKILL_TEMPLATE_FILE = HERE / "core" / "SKILL_TEMPLATE.md"
REFINEMENT_PROMPT_FILE = HERE / "templates" / "refinement_prompt.md"
SYNTHESIS_PROMPT_FILE = HERE / "templates" / "synthesis_prompt.md"
EVALUATION_DIMENSIONS_FILE = HERE / "core" / "EVALUATION_DIMENSIONS.md"


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
    """
    Returns stats about the processed corpus for use in prompts and SKILL.md metadata.
    Effective tokens = prose_tokens * (confidence / 5) per document.
    """
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
    """
    Returns the fractional influence of a new document relative to the existing corpus.
    influence = (new_effective_tokens) / (corpus_effective_tokens + new_effective_tokens)

    A document added to a 200k effective-token corpus with 10k effective tokens
    gets ~5% influence. This is shown to Claude explicitly to prevent overweighting.
    """
    new_effective = new_doc.get("prose_tokens", 0) * new_doc.get("confidence", 3) / 5.0
    corpus_effective = corpus_stats["effective_tokens"]
    if corpus_effective + new_effective == 0:
        return 1.0
    return new_effective / (corpus_effective + new_effective)


# ---------------------------------------------------------------------------
# Collect unrefined notes
# ---------------------------------------------------------------------------

def get_unrefined_notes(state: dict) -> list[dict]:
    """Return processed documents whose notes haven't been incorporated into SKILL.md yet."""
    return [
        d for d in state["documents"]
        if d.get("processed") and not d.get("refined_into_skill")
    ]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def build_bootstrap_prompt(state: dict) -> str:
    """First-time synthesis prompt — all notes, no existing SKILL.md."""
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

    prompt = f"""---
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
    return prompt


def build_refinement_prompt(new_notes_docs: list[dict], state: dict) -> str:
    """Refinement prompt — new notes compared against existing SKILL.md."""
    refinement_prompt_template = load_file(REFINEMENT_PROMPT_FILE, "refinement_prompt.md")
    current_skill = load_file(SKILL_FILE, "SKILL.md")
    corpus_stats = compute_corpus_stats(state)
    docs_by_id = {d["id"]: d for d in state["documents"]}

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

    prompt = f"""---
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
    return prompt


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

CONFLICT_MARKER = "## CONFLICT REVIEW"


def detect_conflict(response_text: str) -> bool:
    return CONFLICT_MARKER in response_text


def print_conflict(response_text: str) -> None:
    """Extract and print the conflict review block from Claude's response."""
    idx = response_text.find(CONFLICT_MARKER)
    print("\n" + "=" * 68)
    print("CONFLICT DETECTED — Review required before SKILL.md is updated")
    print("=" * 68)
    print(response_text[idx:])
    print("=" * 68)
    print("\nTo resolve:")
    print("  1. Review the conflict above")
    print("  2. Edit the batch notes or SKILL.md as appropriate")
    print("  3. Rerun: python refine.py --apply SKILL.md <response_file>")
    print("     with a revised Claude response that resolves the conflict")


# ---------------------------------------------------------------------------
# Apply response to SKILL.md
# ---------------------------------------------------------------------------

def cmd_apply(skill_path: str, response_file: str, state: dict) -> None:
    """
    Write Claude's response to SKILL.md (after conflict check).
    Mark contributing documents as refined_into_skill.
    """
    response_path = Path(response_file)
    if not response_path.exists():
        print(f"ERROR: Response file not found: {response_path}")
        sys.exit(1)

    response_text = response_path.read_text(encoding="utf-8")

    if detect_conflict(response_text):
        print_conflict(response_text)
        print("\nSKILL.md was NOT updated. Resolve the conflict first.")
        return

    # Write SKILL.md
    out_path = Path(skill_path)
    out_path.write_text(response_text, encoding="utf-8")
    print(f"SKILL.md updated: {out_path}")

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Prepare refinement or synthesis prompts for SKILL.md."
    )
    parser.add_argument("--notes", metavar="FILE",
                        help="Specific batch notes file to refine against current SKILL.md")
    parser.add_argument("--bootstrap", action="store_true",
                        help="Generate first-time synthesis prompt from all processed notes")
    parser.add_argument("--apply", nargs=2, metavar=("SKILL_FILE", "RESPONSE_FILE"),
                        help="Apply Claude's response to SKILL.md (after conflict check)")
    parser.add_argument("--output", metavar="FILE",
                        help="Write prompt to file instead of stdout")
    args = parser.parse_args()

    state = load_state()

    if args.apply:
        cmd_apply(args.apply[0], args.apply[1], state)
        return

    datestamp = datetime.now().strftime("%Y-%m-%d")
    new_docs = []  # tracks which docs are being incorporated, for filename construction

    if args.bootstrap:
        prompt = build_bootstrap_prompt(state)
    elif args.notes:
        # Find the doc entry for this notes file
        matching = [
            d for d in state["documents"]
            if d.get("batch_notes_file") == args.notes or
               d.get("batch_notes_file") == str(Path(args.notes))
        ]
        if not matching:
            print(f"ERROR: No document found with notes file: {args.notes}")
            print("Make sure you ran: python extract.py --mark-done DOC_ID NOTES_FILE")
            sys.exit(1)
        new_docs = matching
        prompt = build_refinement_prompt(matching, state)
    else:
        # Default: all unrefined processed documents
        unrefined = get_unrefined_notes(state)
        if not unrefined:
            print("No unrefined batch notes found.")
            print("All processed documents have been incorporated into SKILL.md.")
            print("To add new documents: python corpus.py --add <path>")
            return
        if not SKILL_FILE.exists():
            print("No SKILL.md found. Run with --bootstrap for first-time synthesis.")
            return
        new_docs = unrefined
        prompt = build_refinement_prompt(unrefined, state)

    # Determine default output filename — includes doc IDs and datestamp so
    # generated files are never silently overwritten between runs.
    # Generated prompts land in /prompts; templates live in /templates.
    PROMPTS_DIR = HERE / "prompts"
    PROMPTS_DIR.mkdir(exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    elif args.bootstrap:
        out_path = PROMPTS_DIR / f"bootstrap_prompt_{datestamp}.md"
    else:
        doc_slug = "+".join(d["id"] for d in new_docs)
        out_path = PROMPTS_DIR / f"refinement_prompt_{doc_slug}_{datestamp}.md"

    out_path.write_text(prompt, encoding="utf-8")
    print(f"Prompt written to: {out_path}")
    print(f"Upload {out_path.name} to Claude → save response as SKILL.md")


if __name__ == "__main__":
    main()
