"""
corpus.py
---------
Manages the corpus state for voice extraction. Registers documents,
counts tokens, and reports what needs processing.

State is stored in corpus_state.yaml alongside this script.
Edit that file by hand if needed — it is plain YAML.

Usage:
    python corpus.py                          # show current status

    # Add a single document with metadata in one command
    python corpus.py --add paper.pdf --type journal_paper --confidence 5 --notes "sole author"

    # Add a directory (defaults applied; update metadata afterward)
    python corpus.py --add pdfs/

    # Update metadata on already-registered documents
    python corpus.py --set-type DOC_ID journal_paper
    python corpus.py --set-confidence DOC_ID 5
    python corpus.py --set-notes DOC_ID "sole author, high signal"

Document types:
    journal_paper, proposal, research_statement, letter_of_rec,
    review_perspective, technical_email, other

Confidence scale (1-5):
    5 — Exemplary: clearest expression of voice
    4 — Strong: clearly yours, minor stylistic compromises
    3 — Typical: representative but unremarkable
    2 — Weak: constrained by format, audience, or early career period
    1 — Marginal: include for coverage only

Dependencies:
    pip install pymupdf tiktoken pyyaml
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import fitz
import tiktoken
import yaml

STATE_FILE = Path("corpus_state.yaml")
ENCODING = tiktoken.get_encoding("cl100k_base")

VALID_TYPES = [
    "journal_paper", "proposal", "research_statement",
    "letter_of_rec", "review_perspective", "technical_email", "other"
]

DEFAULT_TYPE_FOR_SUFFIX = {
    ".pdf": "journal_paper",
    ".txt": "technical_email",
}


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"documents": []}
    with open(STATE_FILE) as f:
        state = yaml.safe_load(f) or {}
    state.setdefault("documents", [])
    return state


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

def extract_text(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        try:
            doc = fitz.open(filepath)
            pages = [page.get_text() for page in doc]
            doc.close()
            return "\n".join(pages)
        except Exception as e:
            print(f"  WARNING: Could not extract text from {filepath}: {e}")
            return ""
    elif suffix == ".txt":
        try:
            return filepath.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  WARNING: Could not read {filepath}: {e}")
            return ""
    else:
        return ""


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


# ---------------------------------------------------------------------------
# Document ID generation
# ---------------------------------------------------------------------------

def make_doc_id(filepath: Path, existing_ids: set) -> str:
    base_id = filepath.stem.lower().replace(" ", "_").replace("-", "_")
    doc_id = base_id
    counter = 2
    while doc_id in existing_ids:
        doc_id = f"{base_id}_{counter}"
        counter += 1
    return doc_id


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_type(doc_type: str) -> str:
    if doc_type not in VALID_TYPES:
        print(f"ERROR: Invalid type '{doc_type}'.")
        print(f"  Valid types: {', '.join(VALID_TYPES)}")
        sys.exit(1)
    return doc_type


def validate_confidence(conf_str: str) -> int:
    try:
        confidence = int(conf_str)
        if not 1 <= confidence <= 5:
            raise ValueError
        return confidence
    except ValueError:
        print("ERROR: Confidence must be an integer between 1 and 5.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(paths, state, doc_type=None, confidence=None, notes=""):
    """
    Register one or more files or directories.

    If --type / --confidence / --notes are supplied alongside --add,
    they apply to every file being added in this invocation. This is
    most useful when adding a single file. When adding a directory,
    use the --set-* commands afterward to tune individual documents.
    """
    existing_ids = {d["id"] for d in state["documents"]}
    existing_paths = {d["filepath"] for d in state["documents"]}
    added = 0

    files_to_add = []
    for path_str in paths:
        p = Path(path_str)
        if p.is_dir():
            files_to_add.extend(sorted(p.glob("*.pdf")))
            files_to_add.extend(sorted(p.glob("*.txt")))
        elif p.exists():
            files_to_add.append(p)
        else:
            print(f"  WARNING: Path not found: {p}")

    if not files_to_add:
        print("No files found to add.")
        return

    for filepath in files_to_add:
        filepath_str = str(filepath)

        if filepath_str in existing_paths:
            print(f"  SKIP (already registered): {filepath.name}")
            continue

        doc_id = make_doc_id(filepath, existing_ids)

        print(f"  Counting tokens: {filepath.name} ...", end=" ", flush=True)
        text = extract_text(filepath)
        tokens = count_tokens(text) if text.strip() else 0
        print(f"{tokens:,} tokens")

        resolved_type = doc_type or DEFAULT_TYPE_FOR_SUFFIX.get(filepath.suffix.lower(), "other")
        resolved_confidence = confidence or 3

        entry = {
            "id": doc_id,
            "filepath": filepath_str,
            "type": resolved_type,
            "confidence": resolved_confidence,
            "prose_tokens": tokens,
            "processed": False,
            "batch_notes_file": None,
            "refined_into_skill": False,
            "added": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes,
        }
        state["documents"].append(entry)
        existing_ids.add(doc_id)
        existing_paths.add(filepath_str)

        print(f"  -> Registered: {doc_id}  |  type: {resolved_type}  |  confidence: {resolved_confidence}/5")
        if notes:
            print(f"     notes: {notes}")
        added += 1

    save_state(state)
    print(f"\nAdded {added} document(s) to corpus_state.yaml.")

    if not doc_type or not confidence:
        print("Tip: review status with 'python corpus.py' and update any defaults with --set-* commands.")


def cmd_set_type(doc_id, doc_type, state):
    doc_type = validate_type(doc_type)
    for doc in state["documents"]:
        if doc["id"] == doc_id:
            doc["type"] = doc_type
            save_state(state)
            print(f"Updated type for '{doc_id}': {doc_type}")
            return
    print(f"ERROR: Document ID not found: '{doc_id}'")
    print("Run 'python corpus.py' to see registered IDs.")


def cmd_set_confidence(doc_id, conf_str, state):
    confidence = validate_confidence(conf_str)
    for doc in state["documents"]:
        if doc["id"] == doc_id:
            doc["confidence"] = confidence
            save_state(state)
            print(f"Updated confidence for '{doc_id}': {confidence}/5")
            return
    print(f"ERROR: Document ID not found: '{doc_id}'")
    print("Run 'python corpus.py' to see registered IDs.")


def cmd_set_notes(doc_id, notes, state):
    for doc in state["documents"]:
        if doc["id"] == doc_id:
            doc["notes"] = notes
            save_state(state)
            print(f"Updated notes for '{doc_id}'.")
            return
    print(f"ERROR: Document ID not found: '{doc_id}'")
    print("Run 'python corpus.py' to see registered IDs.")


def cmd_status(state):
    docs = state["documents"]
    if not docs:
        print("No documents registered.")
        print("Add documents with: python corpus.py --add <path> [--type TYPE] [--confidence N] [--notes TEXT]")
        return

    processed = [d for d in docs if d.get("processed")]
    unprocessed = [d for d in docs if not d.get("processed")]
    refined = [d for d in docs if d.get("refined_into_skill")]

    effective_tokens = sum(
        d.get("prose_tokens", 0) * d.get("confidence", 3) / 5.0
        for d in processed
    )

    print("=" * 72)
    print("CORPUS STATUS")
    print(f"  Total documents   : {len(docs)}")
    print(f"  Processed         : {len(processed)}")
    print(f"  Incorporated      : {len(refined)}  (refined into SKILL.md)")
    print(f"  Unprocessed       : {len(unprocessed)}")
    print(f"  Raw tokens        : {sum(d.get('prose_tokens', 0) for d in processed):,}  (processed docs)")
    print(f"  Effective tokens  : {effective_tokens:,.0f}  (confidence-weighted)")
    print("=" * 72)

    if unprocessed:
        print("\nUNPROCESSED  (sorted by priority: confidence down, tokens down)")
        print(f"  {'ID':<40} {'TYPE':<22} {'CONF':>5}  {'TOKENS':>8}")
        print(f"  {'-'*40} {'-'*22} {'-'*5}  {'-'*8}")
        unprocessed_sorted = sorted(
            unprocessed,
            key=lambda d: (-d.get("confidence", 3), -d.get("prose_tokens", 0))
        )
        for d in unprocessed_sorted:
            conf_stars = "*" * d["confidence"] + "-" * (5 - d["confidence"])
            notes_str = f"  <- {d['notes']}" if d.get("notes") else ""
            print(f"  {d['id']:<40} {d['type']:<22} {conf_stars}  {d.get('prose_tokens', 0):>8,}{notes_str}")

    if processed:
        print("\nPROCESSED")
        for d in processed:
            refined_flag = " [in SKILL.md]" if d.get("refined_into_skill") else " [pending refine.py]"
            notes_file = d.get("batch_notes_file") or "?"
            print(f"  {d['id']:<40} -> {notes_file}{refined_flag}")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Manage corpus state for voice extraction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python corpus.py
  python corpus.py --add paper.pdf --type journal_paper --confidence 5 --notes "sole author"
  python corpus.py --add pdfs/
  python corpus.py --set-type smith_2019 proposal
  python corpus.py --set-confidence smith_2019 4
  python corpus.py --set-notes smith_2019 "first author; methods section co-written"
        """
    )

    parser.add_argument("--add", nargs="+", metavar="PATH",
                        help="Register one or more files or directories")
    parser.add_argument("--type", dest="doc_type", metavar="TYPE",
                        help="Document type for --add (" + ", ".join(VALID_TYPES) + ")")
    parser.add_argument("--confidence", metavar="N",
                        help="Confidence 1-5 for --add")
    parser.add_argument("--notes", metavar="TEXT",
                        help="Notes string for --add or --set-notes")

    parser.add_argument("--set-type", nargs=2, metavar=("DOC_ID", "TYPE"),
                        help="Update document type for an existing document")
    parser.add_argument("--set-confidence", nargs=2, metavar=("DOC_ID", "N"),
                        help="Update confidence for an existing document")
    parser.add_argument("--set-notes", nargs=2, metavar=("DOC_ID", "TEXT"),
                        help="Update notes for an existing document")

    args = parser.parse_args()
    state = load_state()

    if args.add:
        doc_type = validate_type(args.doc_type) if args.doc_type else None
        confidence = validate_confidence(args.confidence) if args.confidence else None
        cmd_add(
            paths=args.add,
            state=state,
            doc_type=doc_type,
            confidence=confidence,
            notes=args.notes or "",
        )
    elif args.set_type:
        cmd_set_type(args.set_type[0], args.set_type[1], state)
    elif args.set_confidence:
        cmd_set_confidence(args.set_confidence[0], args.set_confidence[1], state)
    elif args.set_notes:
        cmd_set_notes(args.set_notes[0], args.set_notes[1], state)
    else:
        cmd_status(state)


if __name__ == "__main__":
    main()
