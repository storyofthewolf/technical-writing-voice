#!/usr/bin/env python

"""
corpus.py
---------
Manages one corpus's state for voice extraction. Registers documents, counts
tokens, and reports what needs processing.

Each corpus keeps its state in corpora/<name>/corpus_state.yaml (see paths.py).
Edit that file by hand if needed; it is plain YAML. Select the corpus with
--corpus NAME or --profile NAME (default: the default profile's corpus).

Usage:
    python corpus.py [--corpus NAME]                 # show current status

    # Add a single document with metadata in one command
    python corpus.py --add paper.pdf --type journal_paper --notes "sole author"

    # Add a directory (every .pdf, .docx, .txt; update metadata afterward)
    python corpus.py --corpus NAME --add ~/path/to/columns --type column

    # Update metadata on already-registered documents
    python corpus.py --set-type DOC_ID journal_paper
    python corpus.py --set-notes DOC_ID "sole author, high signal"

    # Hold a document out of extraction and synthesis (for blind validation)
    python corpus.py --set-holdout DOC_ID on|off

Document types are defined per corpus in profiles.yaml (`doc_types`).

All documents contribute evenly to synthesis. Token counts are recorded as
informational corpus-size metadata only; they are not used as weights.

Dependencies:
    uv pip install pymupdf tiktoken pyyaml python-docx
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import tiktoken
import yaml

from extract import SUPPORTED_SUFFIXES, extract_text
from paths import add_selector_args, load_corpus, read_yaml, write_yaml

ENCODING = tiktoken.get_encoding("cl100k_base")

# The corpus selected for this run. Set in main(); save_state()/load_state()
# use it so skill.py and archive.py can import them unchanged.
_CORPUS = None


def set_corpus(corpus) -> None:
    global _CORPUS
    _CORPUS = corpus


def _corpus():
    if _CORPUS is None:
        set_corpus(load_corpus())
    return _CORPUS


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def load_state() -> dict:
    state = read_yaml(_corpus().state_file, {}) or {}
    state.setdefault("documents", [])
    return state


def save_state(state: dict) -> None:
    write_yaml(_corpus().state_file, state)


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


# ---------------------------------------------------------------------------
# Document ID generation
# ---------------------------------------------------------------------------

def make_doc_id(filepath: Path, existing_ids: set) -> str:
    base_id = filepath.stem.lower()
    for ch in " -/.":
        base_id = base_id.replace(ch, "_")
    while "__" in base_id:
        base_id = base_id.replace("__", "_")
    base_id = base_id.strip("_")
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
    valid = _corpus().doc_types
    if doc_type not in valid:
        print(f"ERROR: Invalid type '{doc_type}' for corpus '{_corpus().name}'.")
        print(f"  Valid types: {', '.join(valid)}")
        sys.exit(1)
    return doc_type


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(paths, state, doc_type=None, notes=""):
    """
    Register one or more files or directories.

    If --type / --notes are supplied alongside --add, they apply to every file
    being added in this invocation. When adding a directory, use the --set-*
    commands afterward to tune individual documents.
    """
    corpus = _corpus()
    existing_ids = {d["id"] for d in state["documents"]}
    existing_paths = {d["filepath"] for d in state["documents"]}
    added = 0

    files_to_add = []
    for path_str in paths:
        p = Path(path_str).expanduser()
        if p.is_dir():
            for suffix in SUPPORTED_SUFFIXES:
                files_to_add.extend(sorted(
                    f for f in p.glob(f"*{suffix}") if not f.name.startswith("~$")))
        elif p.exists():
            files_to_add.append(p)
        else:
            print(f"  WARNING: Path not found: {p}")

    if not files_to_add:
        print("No files found to add.")
        return

    for filepath in files_to_add:
        filepath_str = str(filepath.resolve())

        if filepath_str in existing_paths or str(filepath) in existing_paths:
            print(f"  SKIP (already registered): {filepath.name}")
            continue

        doc_id = make_doc_id(filepath, existing_ids)

        print(f"  Counting tokens: {filepath.name} ...", end=" ", flush=True)
        text = extract_text(filepath)
        tokens = count_tokens(text) if text.strip() else 0
        print(f"{tokens:,} tokens")

        resolved_type = doc_type or corpus.default_type_for_suffix.get(
            filepath.suffix.lower(), "other")

        entry = {
            "id": doc_id,
            "filepath": filepath_str,
            "type": resolved_type,
            "prose_tokens": tokens,
            "processed": False,
            "batch_notes_file": None,
            "added": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes,
        }
        state["documents"].append(entry)
        existing_ids.add(doc_id)
        existing_paths.add(filepath_str)

        print(f"  -> Registered: {doc_id}  |  type: {resolved_type}")
        if notes:
            print(f"     notes: {notes}")
        added += 1

    save_state(state)
    print(f"\nAdded {added} document(s) to corpus '{corpus.name}'.")

    if not doc_type:
        print("Tip: review status with 'python corpus.py' and set types with --set-type.")


def _find(state, doc_id):
    for doc in state["documents"]:
        if doc["id"] == doc_id:
            return doc
    print(f"ERROR: Document ID not found in corpus '{_corpus().name}': '{doc_id}'")
    print("Run 'python corpus.py' to see registered IDs.")
    sys.exit(1)


def cmd_set_type(doc_id, doc_type, state):
    doc_type = validate_type(doc_type)
    _find(state, doc_id)["type"] = doc_type
    save_state(state)
    print(f"Updated type for '{doc_id}': {doc_type}")


def cmd_set_notes(doc_id, notes, state):
    _find(state, doc_id)["notes"] = notes
    save_state(state)
    print(f"Updated notes for '{doc_id}'.")


def cmd_set_holdout(doc_id, value, state):
    doc = _find(state, doc_id)
    on = value == "on"
    if on and doc.get("processed"):
        print(f"WARNING: '{doc_id}' is already extracted. Holding it out now "
              "excludes it from future synthesis, but its notes may already be "
              "in the built skill. Rebuild (bootstrap) for a clean holdout.")
    if on:
        doc["holdout"] = True
    else:
        doc.pop("holdout", None)
    save_state(state)
    print(f"Holdout for '{doc_id}': {'on' if on else 'off'}")


def _parse_notes_header(path: Path) -> dict:
    """Read the YAML front-matter header from a notes file.

    Extraction (the /extract-voice-notes skill) stamps each notes file with how
    it was made. A per-document file names one doc; a batch file names several:

        ---
        doc_id: wolf2025psj            # per-document
        doc_ids: [a, b, c]             # batch
        extracted: 2026-06-23
        model: claude-opus-4-8
        ---

    Returns {} for headerless notes (e.g. legacy files); the caller treats a
    missing model as 'unknown'. Never raises; a malformed header is ignored.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    try:
        meta = yaml.safe_load(block)
    except yaml.YAMLError:
        return {}
    return meta if isinstance(meta, dict) else {}


def _notes_sources(corpus) -> dict:
    """Map doc_id -> (notes path, header) for every notes file in the corpus.
    A batch notes file maps each doc in its `doc_ids` to the same file. A
    per-document notes_{doc}.md wins over a batch file for the same doc."""
    found = {}
    d = corpus.batch_notes_dir
    if not d.exists():
        return found
    for path in sorted(d.glob("notes_*.md")):
        header = _parse_notes_header(path)
        ids = header.get("doc_ids")
        if isinstance(ids, list):
            for doc_id in ids:
                found.setdefault(str(doc_id), (path, header))
    for path in sorted(d.glob("notes_*.md")):
        doc_id = path.stem[len("notes_"):]
        header = _parse_notes_header(path)
        if not isinstance(header.get("doc_ids"), list):
            found[doc_id] = (path, header)
    return found


def _auto_mark_done(state: dict) -> None:
    """Detect completed extractions and sync extraction metadata from the notes
    file header. Runs on every status call so headers stay authoritative even
    for already-processed documents (a re-extraction with a new model updates
    the recorded model on the next status check)."""
    corpus = _corpus()
    sources = _notes_sources(corpus)
    today = datetime.now().strftime("%Y-%m-%d")
    changed = False
    for doc in state["documents"]:
        doc_id = doc["id"]
        if doc_id not in sources:
            continue
        path, header = sources[doc_id]
        rel = corpus.relative(path)

        # Mark processed the first time a notes file covers this doc.
        if not doc.get("processed"):
            doc["processed"] = True
            doc["processed_date"] = today
            changed = True
            print(f"  [auto-marked done] {doc_id} -> {rel}")
        if doc.get("batch_notes_file") != rel:
            doc["batch_notes_file"] = rel
            changed = True

        # Sync extraction provenance from the notes header (source of truth).
        hdr_model = header.get("model")
        hdr_date = header.get("extracted")
        if hdr_model and doc.get("extraction_model") != hdr_model:
            doc["extraction_model"] = hdr_model
            changed = True
        if hdr_date:
            hdr_date = str(hdr_date)
            if doc.get("extracted_date") != hdr_date:
                doc["extracted_date"] = hdr_date
                changed = True
    if changed:
        save_state(state)


def cmd_pending(state, types=None):
    """Emit the IDs of documents needing extraction, one per line, for the
    /extract-voice-notes skill to consume. A document is pending if no notes
    file covers it yet and it is not held out. Optionally filter to one or more
    document types."""
    _auto_mark_done(state)
    pending = [d for d in state["documents"]
               if not d.get("processed") and not d.get("holdout")]
    if types:
        pending = [d for d in pending if d.get("type") in types]
    for d in pending:
        print(d["id"])


def cmd_info():
    """Print the selected corpus's resolved settings (for the project skills)."""
    c = _corpus()
    from paths import HERE
    rel = lambda p: str(Path(p).relative_to(HERE))
    print(f"corpus: {c.name}")
    print(f"root: {rel(c.root)}")
    print(f"extraction_mode: {c.extraction_mode}")
    print(f"extraction_template: {rel(c.extraction_template)}")
    print(f"dimensions: {rel(c.dimensions_file)}")
    print(f"doc_types: {', '.join(c.doc_types)}")
    print(f"batch_notes_dir: {rel(c.batch_notes_dir)}")
    print(f"stripped_text_dir: {rel(c.stripped_text_dir)}")
    print(f"validation_dir: {rel(c.validation_dir)}")


def _discovered_profiles(docs) -> list[str]:
    """Profile names inferred from per-profile refinement flags present in the
    corpus data (skill.py writes `refined_into_skill_<profile>`)."""
    seen = []
    for d in docs:
        for key in d:
            if key.startswith("refined_into_skill_"):
                name = key[len("refined_into_skill_"):]
                if name not in seen:
                    seen.append(name)
    return seen


def cmd_status(state):
    _auto_mark_done(state)
    corpus = _corpus()
    docs = state["documents"]
    if not docs:
        print(f"No documents registered in corpus '{corpus.name}'.")
        print("Add documents with: python corpus.py --corpus NAME --add <path> [--type TYPE]")
        return

    processed = [d for d in docs if d.get("processed")]
    holdout = [d for d in docs if d.get("holdout")]
    unprocessed = [d for d in docs if not d.get("processed") and not d.get("holdout")]
    profiles = _discovered_profiles(docs)

    print("=" * 72)
    print(f"CORPUS STATUS  [{corpus.name}]  ({corpus.extraction_mode} extraction)")
    print(f"  Total documents   : {len(docs)}")
    print(f"  Processed         : {len(processed)}")
    for prof in profiles:
        flag = f"refined_into_skill_{prof}"
        n = sum(1 for d in docs if d.get(flag))
        print(f"  Incorporated [{prof}] : {n}  (built into the {prof} skill)")
    if not profiles:
        print("  Incorporated      : 0  (no profile built yet)")
    print(f"  Unprocessed       : {len(unprocessed)}")
    if holdout:
        print(f"  Held out          : {len(holdout)}  (excluded from extraction and synthesis)")
    print(f"  Raw tokens        : {sum(d.get('prose_tokens', 0) for d in processed):,}  (processed docs; informational)")
    print("=" * 72)

    if unprocessed:
        print("\nUNPROCESSED  (sorted by token count)")
        print(f"  {'ID':<40} {'TYPE':<22}  {'TOKENS':>8}")
        print(f"  {'-'*40} {'-'*22}  {'-'*8}")
        for d in sorted(unprocessed, key=lambda d: -d.get("prose_tokens", 0)):
            notes_str = f"  <- {d['notes']}" if d.get("notes") else ""
            print(f"  {d['id']:<40} {d['type']:<22}  {d.get('prose_tokens', 0):>8,}{notes_str}")

    if holdout:
        print("\nHELD OUT")
        for d in holdout:
            print(f"  {d['id']:<40} {d['type']:<22}  {d.get('prose_tokens', 0):>8,}")

    if processed:
        print("\nPROCESSED")
        for d in processed:
            if profiles:
                built = [p for p in profiles if d.get(f"refined_into_skill_{p}")]
                refined_flag = f"  [in: {', '.join(built)}]" if built else "  [pending skill.py]"
            else:
                refined_flag = "  [pending skill.py]"
            notes_file = d.get("batch_notes_file") or "?"
            model = _short_model(d.get("extraction_model"))
            date = d.get("extracted_date") or d.get("processed_date") or "?"
            provenance = f"  [{model}, {date}]"
            print(f"  {d['id']:<40} -> {notes_file}{provenance}{refined_flag}")

    print()


def _short_model(model_id) -> str:
    """Abbreviate a full model id for display (claude-opus-4-8 -> opus-4-8).
    Headerless / legacy notes have no recorded model -> 'unknown'."""
    if not model_id:
        return "model: unknown"
    m = str(model_id)
    for family in ("opus", "sonnet", "haiku", "fable"):
        if family in m:
            idx = m.find(family)
            return m[idx:]
    return m


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Manage one corpus's state for voice extraction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python corpus.py
  python corpus.py --corpus NAME --add ~/path/to/columns --type column
  python corpus.py --set-type smith_2019 proposal
  python corpus.py --set-notes smith_2019 "first author"
  python corpus.py --corpus NAME --set-holdout DOC_ID on
  python corpus.py --profile gr --info
        """
    )
    add_selector_args(parser)

    parser.add_argument("--add", nargs="+", metavar="PATH",
                        help="Register one or more files or directories")
    parser.add_argument("--type", dest="doc_type", metavar="TYPE",
                        help="Document type for --add (see the corpus's doc_types)")
    parser.add_argument("--notes", metavar="TEXT",
                        help="Notes string for --add or --set-notes")

    parser.add_argument("--set-type", nargs=2, metavar=("DOC_ID", "TYPE"),
                        help="Update document type for an existing document")
    parser.add_argument("--set-notes", nargs=2, metavar=("DOC_ID", "TEXT"),
                        help="Update notes for an existing document")
    parser.add_argument("--set-holdout", nargs=2, metavar=("DOC_ID", "on|off"),
                        help="Hold a document out of extraction and synthesis")
    parser.add_argument("--pending", action="store_true",
                        help="Print IDs of documents needing extraction, one per line")
    parser.add_argument("--pending-types", nargs="+", metavar="TYPE",
                        help="With --pending: restrict to these document types")
    parser.add_argument("--info", action="store_true",
                        help="Print the selected corpus's resolved settings")

    args = parser.parse_args()
    set_corpus(load_corpus(args.corpus, args.profile))

    if args.info:
        cmd_info()
        return

    state = load_state()

    if args.add:
        doc_type = validate_type(args.doc_type) if args.doc_type else None
        cmd_add(paths=args.add, state=state, doc_type=doc_type, notes=args.notes or "")
    elif args.pending:
        cmd_pending(state, types=args.pending_types)
    elif args.set_type:
        cmd_set_type(args.set_type[0], args.set_type[1], state)
    elif args.set_notes:
        cmd_set_notes(args.set_notes[0], args.set_notes[1], state)
    elif args.set_holdout:
        if args.set_holdout[1] not in ("on", "off"):
            print("ERROR: --set-holdout takes 'on' or 'off'.")
            sys.exit(1)
        cmd_set_holdout(args.set_holdout[0], args.set_holdout[1], state)
    else:
        cmd_status(state)


if __name__ == "__main__":
    main()
