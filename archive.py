#!/usr/bin/env python

"""
archive.py
----------
Snapshot the current pipeline state into archive/run_YYYY-MM-DD_HHMMSS[_label]/.

Copies SKILL.md, batch_notes/, and corpus_state.yaml. Never touches overrides.yaml.

Usage:
    python archive.py                          # snapshot only
    python archive.py --label before_refine    # snapshot with a label suffix
    python archive.py --reset soft             # snapshot, then reset SKILL.md
    python archive.py --reset full             # snapshot, then full reset

Reset modes:
    soft  — delete SKILL.md; set refined_into_skill=False on all docs;
            leave processed flags and batch notes untouched.
    full  — delete SKILL.md; delete batch_notes/; reset all docs to
            processed=False, refined_into_skill=False; clear batch_notes_file
            and processed_date fields.

Dependencies:
    pyyaml
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ARCHIVE_DIR = HERE / "archive"
SKILL_FILE = HERE / "SKILL.md"
BATCH_NOTES_DIR = HERE / "batch_notes"
STATE_FILE = HERE / "corpus_state.yaml"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"documents": []}
    with open(STATE_FILE) as f:
        return yaml.safe_load(f) or {"documents": []}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def make_run_dir(label: str) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    name = f"run_{stamp}_{label}" if label else f"run_{stamp}"
    run_dir = ARCHIVE_DIR / name
    run_dir.mkdir(parents=True)
    return run_dir


def do_snapshot(run_dir: Path) -> None:
    copied = []

    if SKILL_FILE.exists():
        shutil.copy2(SKILL_FILE, run_dir / SKILL_FILE.name)
        copied.append(SKILL_FILE.name)

    if BATCH_NOTES_DIR.exists():
        shutil.copytree(BATCH_NOTES_DIR, run_dir / BATCH_NOTES_DIR.name)
        copied.append(f"{BATCH_NOTES_DIR.name}/")

    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, run_dir / STATE_FILE.name)
        copied.append(STATE_FILE.name)

    if copied:
        print(f"Archived to: {run_dir}")
        for name in copied:
            print(f"  {name}")
    else:
        print(f"Archived to: {run_dir}  (nothing to copy — all sources absent)")


def do_reset_soft() -> None:
    if SKILL_FILE.exists():
        SKILL_FILE.unlink()
        print("Deleted SKILL.md")
    else:
        print("SKILL.md not found — skipping delete")

    state = load_state()
    updated = 0
    for doc in state["documents"]:
        if doc.get("refined_into_skill"):
            doc["refined_into_skill"] = False
            doc.pop("refined_date", None)
            updated += 1
    save_state(state)
    print(f"Reset refined_into_skill on {updated} document(s)")


def do_reset_full() -> None:
    if SKILL_FILE.exists():
        SKILL_FILE.unlink()
        print("Deleted SKILL.md")
    else:
        print("SKILL.md not found — skipping delete")

    if BATCH_NOTES_DIR.exists():
        shutil.rmtree(BATCH_NOTES_DIR)
        print(f"Deleted {BATCH_NOTES_DIR.name}/")
    else:
        print(f"{BATCH_NOTES_DIR.name}/ not found — skipping delete")

    state = load_state()
    for doc in state["documents"]:
        doc["processed"] = False
        doc["refined_into_skill"] = False
        doc["batch_notes_file"] = None
        doc.pop("processed_date", None)
        doc.pop("refined_date", None)
    save_state(state)
    print(f"Reset {len(state['documents'])} document(s) to unprocessed state")


def main():
    parser = argparse.ArgumentParser(
        description="Archive pipeline state and optionally reset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python archive.py
  python archive.py --label before_refine
  python archive.py --reset soft
  python archive.py --reset full --label clean_slate
        """
    )
    parser.add_argument("--label", metavar="TEXT", default="",
                        help="Optional suffix appended to the archive folder name")
    parser.add_argument("--reset", choices=["soft", "full"],
                        help="Reset mode to apply after archiving")
    args = parser.parse_args()

    run_dir = make_run_dir(args.label)
    do_snapshot(run_dir)

    if args.reset == "soft":
        print()
        do_reset_soft()
    elif args.reset == "full":
        print()
        do_reset_full()


if __name__ == "__main__":
    main()
