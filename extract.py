#!/usr/bin/env python

"""
extract.py
----------
Strips registered documents to plain text in the corpus's stripped_text/
folder. The model read itself (writing batch_notes/) is done in Claude Code by
the /extract-voice-notes skill, which calls this script first. Nothing here is
pasted anywhere by hand.

Usage:
    python extract.py [--corpus NAME | --profile NAME] DOC_ID [DOC_ID ...]
    python extract.py [--corpus NAME | --profile NAME] --all     # all unprocessed
    python extract.py ... --force DOC_ID      # re-strip even if text exists

Supported inputs: .pdf (cleaned of running heads, references, figure noise),
.docx (paragraphs in order, headings as "## ", list items as "- ", tables as
" | "-joined rows), .txt (as-is).

Dependencies:
    uv pip install pymupdf tiktoken pyyaml python-docx
"""

import argparse
import re
import sys
from pathlib import Path

import fitz

from paths import add_selector_args, load_corpus, read_yaml


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


def extract_text_docx(filepath: Path) -> str:
    """
    Extract a .docx body in document order. Headings become "## text", list
    paragraphs become "- text", and table rows become " | "-joined cells, so
    layout that carries voice (headed sections, bullet lists, results tables)
    survives as plain-text markers. Headers, footers, and comments are not read.
    Boilerplate (letterhead, contact blocks) is kept: the orchestrator's strip
    check flags it rather than this script guessing.
    """
    try:
        import docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError:
        print("  ERROR: python-docx not installed (uv pip install python-docx)")
        return ""
    try:
        document = docx.Document(str(filepath))
    except Exception as e:
        print(f"  WARNING: Could not open {filepath}: {e}")
        return ""

    out = []
    body = document.element.body
    for child in body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            para = Paragraph(child, document)
            text = para.text.strip()
            if not text:
                out.append("")
                continue
            style = (para.style.name if para.style is not None else "") or ""
            is_list = (child.find(".//{*}numPr") is not None
                       or style.lower().startswith("list"))
            if style.lower().startswith(("heading", "title")):
                out.append(f"## {text}")
            elif is_list:
                out.append(f"- {text}")
            else:
                out.append(text)
        elif tag == "tbl":
            table = Table(child, document)
            out.append("")
            for row in table.rows:
                cells = []
                for cell in row.cells:
                    c = " ".join(cell.text.split())
                    if not cells or cells[-1] != c:  # merged cells repeat
                        cells.append(c)
                out.append(" | ".join(cells))
            out.append("")

    # Collapse runs of blank lines.
    result, prev_blank = [], False
    for line in out:
        blank = not line.strip()
        if blank and prev_blank:
            continue
        result.append(line)
        prev_blank = blank
    return "\n".join(result).strip()


def extract_text_txt(filepath: Path) -> str:
    try:
        return filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  WARNING: Could not read {filepath}: {e}")
        return ""


SUPPORTED_SUFFIXES = (".pdf", ".docx", ".txt")


def extract_text(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return extract_text_pdf(filepath)
    elif suffix == ".docx":
        return extract_text_docx(filepath)
    elif suffix == ".txt":
        return extract_text_txt(filepath)
    else:
        print(f"  WARNING: Unsupported file type: {filepath.suffix}")
        return ""


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_strip(doc_ids: list[str], state: dict, corpus, force: bool = False) -> None:
    corpus.stripped_text_dir.mkdir(parents=True, exist_ok=True)
    docs_by_id = {d["id"]: d for d in state["documents"]}

    for doc_id in doc_ids:
        if doc_id not in docs_by_id:
            print(f"ERROR: Document ID not found in corpus '{corpus.name}': {doc_id}")
            continue

        doc = docs_by_id[doc_id]
        filepath = Path(doc["filepath"])
        stripped_path = corpus.stripped_text_dir / f"{doc_id}.txt"

        if stripped_path.exists() and not force:
            print(f"Exists (reusing): {corpus.relative(stripped_path)}")
            continue
        if not filepath.exists():
            print(f"ERROR: Source file not found: {filepath}")
            continue
        print(f"Stripping: {filepath.name} ...", end=" ", flush=True)
        text = extract_text(filepath)
        if not text.strip():
            print("EMPTY — skipping")
            continue
        stripped_path.write_text(text, encoding="utf-8")
        print(f"{len(text):,} chars -> {corpus.relative(stripped_path)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Strip registered corpus documents to plain text."
    )
    add_selector_args(parser)
    parser.add_argument("doc_ids", nargs="*", help="Document IDs to strip")
    parser.add_argument("--all", action="store_true",
                        help="Strip all unprocessed, non-holdout documents")
    parser.add_argument("--force", action="store_true",
                        help="Re-strip even if stripped text already exists")
    args = parser.parse_args()

    corpus = load_corpus(args.corpus, args.profile)
    if not corpus.state_file.exists():
        print(f"ERROR: {corpus.relative(corpus.state_file)} not found in "
              f"{corpus.root}. Run corpus.py --add first.")
        sys.exit(1)
    state = read_yaml(corpus.state_file, {"documents": []})
    state.setdefault("documents", [])

    if args.all:
        ids = [d["id"] for d in state["documents"]
               if not d.get("processed") and not d.get("holdout")]
        if not ids:
            print("All documents processed.")
            return
        cmd_strip(ids, state, corpus, force=args.force)
    elif args.doc_ids:
        cmd_strip(args.doc_ids, state, corpus, force=args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
