"""
extract.py
----------
Strips one or more documents to plain text and writes a ready-to-paste
extraction prompt to batch_notes/. You paste the prompt into a Claude session,
save Claude's response as the batch notes file, then mark the document processed.

Usage:
    python extract.py DOC_ID [DOC_ID ...]    # extract specific documents
    python extract.py --priority              # extract highest-confidence unprocessed doc
    python extract.py --all                  # extract all unprocessed documents

After running:
    1. Open the generated prompt file in batch_notes/prompt_[DOC_ID].md
    2. Paste it into a Claude session (with no other context needed)
    3. Save Claude's full response as batch_notes/notes_[DOC_ID].md
    4. Run: python extract.py --mark-done DOC_ID batch_notes/notes_[DOC_ID].md

Dependencies:
    pip install pymupdf tiktoken pyyaml
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import re

import fitz
import yaml

HERE = Path(__file__).parent
STATE_FILE = HERE / "corpus_state.yaml"
BATCH_NOTES_DIR = HERE / "batch_notes"
STRIPPED_TEXT_DIR = HERE / "stripped_text"
EXTRACTION_PROMPT_FILE = HERE / "templates" / "extraction_prompt.md"


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if not STATE_FILE.exists():
        print("ERROR: corpus_state.yaml not found. Run corpus.py --add first.")
        sys.exit(1)
    with open(STATE_FILE) as f:
        return yaml.safe_load(f) or {"documents": []}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_extraction_prompt() -> str:
    if not EXTRACTION_PROMPT_FILE.exists():
        print(f"ERROR: {EXTRACTION_PROMPT_FILE} not found.")
        sys.exit(1)
    return EXTRACTION_PROMPT_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Text extraction and cleaning
# ---------------------------------------------------------------------------

# Section headings common in scientific papers — keep these even if short
SECTION_HEADINGS = {
    "abstract", "introduction", "background", "motivation",
    "methods", "method", "methodology", "materials and methods",
    "results", "discussion", "conclusions", "conclusion",
    "summary", "acknowledgments", "acknowledgements",
    "appendix", "supplementary", "supplemental",
    "data availability", "code availability", "author contributions",
    "significance", "innovation", "approach", "broader impacts",
    "specific aims", "related work", "future work",
    "experimental setup", "experimental design", "evaluation",
    "model", "modeling", "framework", "theory", "observations",
    "implications", "limitations", "outlook",
}


def is_section_heading(line: str) -> bool:
    """Return True if line looks like a section heading worth keeping."""
    stripped = line.strip().rstrip(".").lower()
    # Exact match or numbered heading like "1. Introduction" or "2.1 Methods"
    if stripped in SECTION_HEADINGS:
        return True
    # Numbered: "1 Introduction", "2.1 Methods", "A. Appendix"
    numbered = re.sub(r'^[\dA-Z]+[\.\d]*\.?\s+', '', stripped)
    if numbered in SECTION_HEADINGS:
        return True
    return False


def looks_like_prose(line: str) -> bool:
    """
    Heuristic: a line is likely prose if it has enough words and
    isn't dominated by numbers/symbols.
    """
    words = line.split()
    if len(words) < 5:
        return False
    # Reject lines that are more than 40% numeric tokens
    numeric = sum(1 for w in words if re.match(r'^[\d\.\,\-\+\(\)\/\%\±]+$', w))
    if numeric / len(words) > 0.4:
        return False
    return True


def clean_pdf_text(raw: str) -> str:
    """
    Multi-pass cleaning pipeline for PDF-extracted text.
    Removes noise while preserving prose and section headings.
    """
    lines = raw.splitlines()
    cleaned = []

    # --- Pass 1: remove references block ---
    # References almost always appear at the end. Find the last occurrence
    # of a line that is just "References" or "Bibliography" and drop everything after.
    ref_cutoff = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip().lower().rstrip(".")
        if stripped in ("references", "bibliography", "works cited", "literature cited"):
            # Only cut if we're past the halfway point (avoid cutting an intro section)
            if i > len(lines) * 0.5:
                ref_cutoff = i
                break
    lines = lines[:ref_cutoff]

    # --- Pass 2: line-by-line filtering ---
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty line — preserve paragraph breaks but collapse multiples later
        if not stripped:
            cleaned.append("")
            i += 1
            continue

        # Always keep section headings
        if is_section_heading(stripped):
            cleaned.append(stripped)
            i += 1
            continue

        # Remove page numbers: isolated integers, possibly with surrounding noise
        if re.match(r'^\d{1,4}$', stripped):
            i += 1
            continue

        # Remove DOIs and URLs
        if re.match(r'^(https?://|doi:|www\.)', stripped, re.IGNORECASE):
            i += 1
            continue
        if re.search(r'10\.\d{4,}/\S+', stripped) and len(stripped.split()) < 6:
            i += 1
            continue

        # Remove email addresses on their own line
        if re.match(r'^[\w\.\+\-]+@[\w\.\-]+\.[a-z]{2,}$', stripped, re.IGNORECASE):
            i += 1
            continue
        if re.search(r'(corresponding author|contact|e-mail|email)[:\s]+[\w\.\+\-]+@', stripped, re.IGNORECASE):
            i += 1
            continue

        # Remove journal running headers/footers: short lines containing
        # volume/page patterns like "Vol. 12, No. 3" or "pp. 123–145"
        if re.search(r'\b(vol\.?|volume|no\.?|pp\.?|pages?)\s*[\d]', stripped, re.IGNORECASE):
            if len(stripped.split()) < 12:
                i += 1
                continue

        # Remove copyright / license lines
        if re.search(r'©|copyright|creative commons|CC BY|all rights reserved', stripped, re.IGNORECASE):
            i += 1
            continue

        # Remove figure/table labels without caption prose:
        # "Figure 3.", "Fig. 3.", "Table 2." alone or with very short trailing text
        if re.match(r'^(fig\.?|figure|table|supplementary figure|extended data)\s*\d+[a-z]?[\.\:]?\s*$',
                    stripped, re.IGNORECASE):
            i += 1
            continue
        # Axis labels: short line ending in a unit in parentheses e.g. "Temperature (K)"
        if re.match(r'^[A-Za-z\s]+\([A-Za-z°µ/\^\d]+\)\s*$', stripped) and len(stripped.split()) < 6:
            i += 1
            continue

        # Remove lines that are purely symbolic / numeric noise:
        # e.g. axis labels, legend entries, data values
        # Heuristic: line has < 5 words AND no alphabetic word longer than 4 chars
        # (real prose always has longer words)
        if len(stripped.split()) < 5:
            has_real_word = any(
                re.match(r'^[a-zA-Z]{5,}$', w) for w in stripped.split()
            )
            if not has_real_word:
                i += 1
                continue

        # Remove author listing blocks near the top of the document.
        # These are hard to identify precisely; use a windowed heuristic:
        # if we're in the first 80 lines and the line matches author-list patterns,
        # skip it. Author lines: comma-separated capitalized names, superscript
        # markers, affiliation-style text (university, department, institute).
        if i < 80:
            if re.search(r'\b(university|institute|department|laboratory|center|centre|'
                         r'nasa|noaa|ncar|nssl|caltech|mit|jpl)\b',
                         stripped, re.IGNORECASE):
                if len(stripped.split()) < 20:  # affiliations are short
                    i += 1
                    continue
            # Lines that are mostly superscript-style markers or just names
            # Pattern: "Author A,1 Author B,2 Author C1,2"
            if re.match(r'^([A-Z][a-z]+\.?\s+){1,4}[A-Z][a-z]+[,\d\*†‡]+', stripped):
                if len(stripped.split()) < 12:
                    i += 1
                    continue
            # Catch "Lastname, F.T.,1 Lastname, F.K.,2" author list style
            if re.search(r'[A-Z]\.[A-Z]\.?,?\s*\d', stripped):
                if len(stripped.split()) < 15:
                    i += 1
                    continue

        # Keep the line
        cleaned.append(line)
        i += 1

    # --- Pass 3: collapse multiple blank lines into one ---
    result = []
    prev_blank = False
    for line in cleaned:
        if line.strip() == "":
            if not prev_blank:
                result.append("")
            prev_blank = True
        else:
            result.append(line)
            prev_blank = False

    return "\n".join(result).strip()


def extract_text_pdf(filepath: Path) -> str:
    """
    Extract prose text from PDF.
    Images are ignored by get_text() automatically.
    Extracted text is passed through clean_pdf_text() to remove noise.
    """
    try:
        doc = fitz.open(filepath)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        raw = "\n".join(pages)
        return clean_pdf_text(raw)
    except Exception as e:
        print(f"  WARNING: Could not extract text from {filepath}: {e}")
        return ""


def extract_text_txt(filepath: Path) -> str:
    try:
        return filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  WARNING: Could not read {filepath}: {e}")
        return ""


def extract_text(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return extract_text_pdf(filepath)
    elif suffix == ".txt":
        return extract_text_txt(filepath)
    else:
        print(f"  WARNING: Unsupported file type: {filepath.suffix}")
        return ""



# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def build_prompt(doc: dict, text: str, extraction_prompt_template: str) -> str:
    """
    Build the full extraction prompt for a single document.
    The document text is embedded directly — no file upload needed.
    """
    header = f"""---
action: extract
output_file: notes_{doc['id']}.md
doc_id: {doc['id']}
doc_type: {doc['type']}
confidence: {doc['confidence']}
generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
notes: {doc.get('notes', '')}
---

"""
    doc_block = f"""## Document: {doc['id']}
**Type:** {doc['type']}
**File:** {doc['filepath']}
**Notes:** {doc.get('notes', '')}

```
{text}
```

---

"""
    return header + doc_block + extraction_prompt_template


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_extract(doc_ids: list[str], state: dict) -> None:
    BATCH_NOTES_DIR.mkdir(exist_ok=True)
    STRIPPED_TEXT_DIR.mkdir(exist_ok=True)
    extraction_prompt = load_extraction_prompt()

    docs_by_id = {d["id"]: d for d in state["documents"]}

    for doc_id in doc_ids:
        if doc_id not in docs_by_id:
            print(f"ERROR: Document ID not found: {doc_id}")
            continue

        doc = docs_by_id[doc_id]
        filepath = Path(doc["filepath"])
        stripped_path = STRIPPED_TEXT_DIR / f"{doc_id}.txt"

        # Reuse saved stripped text if it exists
        if stripped_path.exists():
            print(f"Reusing stripped text: {stripped_path}")
            text = stripped_path.read_text(encoding="utf-8")
        else:
            if not filepath.exists():
                print(f"ERROR: File not found: {filepath}")
                continue
            print(f"Extracting text: {filepath.name} ...", end=" ", flush=True)
            text = extract_text(filepath)
            if not text.strip():
                print("EMPTY — skipping")
                continue
            print(f"{len(text):,} chars")
            stripped_path.write_text(text, encoding="utf-8")
            print(f"  → Stripped text saved: {stripped_path}")

        prompt = build_prompt(doc, text, extraction_prompt)
        prompt_path = BATCH_NOTES_DIR / f"prompt_{doc_id}.md"
        prompt_path.write_text(prompt, encoding="utf-8")

        print(f"  → Prompt written: {prompt_path}")
        print(f"  → Upload {prompt_path.name} to Claude → download notes_{doc_id}.md")
        print(f"  → Then run: python extract.py --mark-done {doc_id} batch_notes/notes_{doc_id}.md")
        print()


def cmd_priority(state: dict) -> None:
    unprocessed = [d for d in state["documents"] if not d.get("processed")]
    if not unprocessed:
        print("All documents processed.")
        return
    # highest confidence, then most tokens
    best = max(unprocessed, key=lambda d: (d.get("confidence", 3), d.get("prose_tokens", 0)))
    print(f"Highest priority unprocessed: {best['id']} (confidence {best['confidence']}, {best.get('prose_tokens', 0):,} tokens)")
    cmd_extract([best["id"]], state)


def cmd_all(state: dict) -> None:
    unprocessed = [d["id"] for d in state["documents"] if not d.get("processed")]
    if not unprocessed:
        print("All documents processed.")
        return
    print(f"Extracting {len(unprocessed)} unprocessed document(s)...\n")
    cmd_extract(unprocessed, state)


def cmd_mark_done(doc_id: str, notes_file: str, state: dict) -> None:
    notes_path = Path(notes_file)
    if not notes_path.exists():
        print(f"ERROR: Notes file not found: {notes_path}")
        sys.exit(1)

    for doc in state["documents"]:
        if doc["id"] == doc_id:
            doc["processed"] = True
            doc["batch_notes_file"] = str(notes_path)
            doc["processed_date"] = datetime.now().strftime("%Y-%m-%d")
            save_state(state)
            print(f"Marked {doc_id} as processed. Notes: {notes_path}")
            return

    print(f"ERROR: Document ID not found: {doc_id}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Prepare extraction prompts for unprocessed corpus documents."
    )
    parser.add_argument("doc_ids", nargs="*", help="Document IDs to extract")
    parser.add_argument("--priority", action="store_true",
                        help="Extract the single highest-priority unprocessed document")
    parser.add_argument("--all", action="store_true",
                        help="Extract all unprocessed documents")
    parser.add_argument("--mark-done", nargs=2, metavar=("DOC_ID", "NOTES_FILE"),
                        help="Mark a document as processed and record its notes file")
    args = parser.parse_args()

    state = load_state()

    if args.mark_done:
        cmd_mark_done(args.mark_done[0], args.mark_done[1], state)
    elif args.priority:
        cmd_priority(state)
    elif args.all:
        cmd_all(state)
    elif args.doc_ids:
        cmd_extract(args.doc_ids, state)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
