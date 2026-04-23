#!/usr/bin/env python

# Usage:
#   python utils/token_report.py --current          # mid-run snapshot from working directory
#   python utils/token_report.py --run archive/run_DIRNAME  # completed archived run
#
# Best practices:
#   - Run --current to gauge token usage while a run is in progress.
#   - Archive before resetting so --run can report on the completed state.
#   - Use --run on completed archived runs for reproducible audits.
#
# Dependencies: tiktoken, pyyaml

import argparse
import sys
from datetime import date
from pathlib import Path

import tiktoken

ROOT = Path(__file__).parent.parent
ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return len(ENCODING.encode(text))


def fmt(n: int) -> str:
    return f"{n:>10,}"


def build_report(base: Path) -> tuple[list[str], int]:
    """Return (report_lines, grand_total)."""
    lines = []

    def h(text: str) -> None:
        lines.append(text)

    def row(label: str, n: int) -> None:
        lines.append(f"  {fmt(n)}  {label}")

    def blank() -> None:
        lines.append("")

    grand_total = 0

    # ── INPUT ────────────────────────────────────────────────────────────────
    h("INPUT TOKENS (files sent to Claude)")
    h("─" * 60)
    blank()

    # Extraction prompts: batch_notes/prompt_*.md
    batch_notes_dir = base / "batch_notes"
    extraction_subtotal = 0
    extraction_rows: list[tuple[str, int]] = []
    if batch_notes_dir.exists():
        for f in sorted(batch_notes_dir.glob("prompt_*.md")):
            # derive doc ID: prompt_{doc_id}.md
            doc_id = f.stem[len("prompt_"):]
            n = count_tokens(f)
            extraction_rows.append((doc_id, n))
            extraction_subtotal += n

    if extraction_rows:
        h("  Extraction prompts (batch_notes/prompt_*.md):")
        for doc_id, n in extraction_rows:
            row(doc_id, n)
        blank()
    else:
        h("  Extraction prompts: (none found)")
        blank()

    row("Subtotal — extraction prompts", extraction_subtotal)
    blank()

    # Bootstrap / refinement prompts: prompts/*.md
    prompts_dir = base / "prompts"
    prompt_subtotal = 0
    prompt_rows: list[tuple[str, int]] = []
    if prompts_dir.exists():
        for f in sorted(prompts_dir.glob("*.md")):
            n = count_tokens(f)
            prompt_rows.append((f.name, n))
            prompt_subtotal += n

    if prompt_rows:
        h("  Bootstrap / refinement prompts (prompts/*.md):")
        for name, n in prompt_rows:
            row(name, n)
        blank()
    else:
        h("  Bootstrap / refinement prompts: (none found)")
        blank()

    row("Subtotal — bootstrap/refinement prompts", prompt_subtotal)
    blank()

    input_total = extraction_subtotal + prompt_subtotal
    row("TOTAL INPUT", input_total)
    grand_total += input_total

    blank()
    blank()

    # ── OUTPUT ───────────────────────────────────────────────────────────────
    h("OUTPUT TOKENS (files received from Claude)")
    h("─" * 60)
    blank()

    # Batch notes: batch_notes/notes_*.md
    notes_subtotal = 0
    notes_rows: list[tuple[str, int]] = []
    if batch_notes_dir.exists():
        for f in sorted(batch_notes_dir.glob("notes_*.md")):
            doc_id = f.stem[len("notes_"):]
            n = count_tokens(f)
            notes_rows.append((doc_id, n))
            notes_subtotal += n

    if notes_rows:
        h("  Batch notes (batch_notes/notes_*.md):")
        for doc_id, n in notes_rows:
            row(doc_id, n)
        blank()
    else:
        h("  Batch notes: (none found)")
        blank()

    row("Subtotal — batch notes", notes_subtotal)
    blank()

    # SKILL.md
    skill_file = base / "SKILL.md"
    skill_tokens = count_tokens(skill_file) if skill_file.exists() else 0
    row("SKILL.md", skill_tokens)
    blank()

    output_total = notes_subtotal + skill_tokens
    row("TOTAL OUTPUT", output_total)
    grand_total += output_total

    blank()
    blank()

    # ── GRAND TOTAL ───────────────────────────────────────────────────────────
    h("=" * 60)
    row("GRAND TOTAL", grand_total)
    h("=" * 60)

    return lines, grand_total


def resolve_base(args: argparse.Namespace) -> tuple[Path, str]:
    """Return (base_dir, run_name) for output file naming."""
    if args.current:
        return ROOT, f"current_{date.today().isoformat()}"
    run_path = Path(args.run)
    if not run_path.is_absolute():
        run_path = ROOT / run_path
    if not run_path.exists():
        print(f"Error: archive directory not found: {run_path}", file=sys.stderr)
        sys.exit(1)
    return run_path, run_path.name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report token counts for a pipeline run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/token_report.py --current
  python utils/token_report.py --run archive/run_2026-04-23_120000
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--current", action="store_true",
                       help="Read from working directory")
    group.add_argument("--run", metavar="DIR",
                       help="Read from a specific archive directory")
    args = parser.parse_args()

    base, run_name = resolve_base(args)

    report_lines, _ = build_report(base)

    utils_dir = Path(__file__).parent
    out_filename = f"token_report_{run_name}.txt"
    out_path = utils_dir / out_filename

    report_text = "\n".join(report_lines) + "\n"
    print(report_text)
    out_path.write_text(report_text, encoding="utf-8")
    print(f"Report written to: {out_path}")


if __name__ == "__main__":
    main()
