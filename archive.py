#!/usr/bin/env python

"""
archive.py
----------
Snapshot one profile's pipeline state into
archive/run_YYYY-MM-DD_HHMMSS[_label]/, then optionally reset it so the next
build starts fresh.

Profile-aware: the profile is resolved from profiles.yaml exactly as skill.py
resolves it (--profile NAME, default: default_profile). The snapshot captures
that profile's real built skill (its `output` path, e.g. skills/paper/SKILL.md),
plus the shared batch_notes/, prompts/, and corpus_state.yaml. Reset clears only
that profile's per-profile refinement flags (refined_into_skill_<profile>).

The orphaned root SKILL.md is never archived, reset, or deleted — it is the
author's personal reference, not a pipeline output. overrides.yaml is likewise
never touched.

Usage:
    python archive.py [--profile NAME]                 # snapshot only
    python archive.py [--profile NAME] --label TEXT     # snapshot with a label
    python archive.py [--profile NAME] --reset soft     # snapshot, then soft reset
    python archive.py [--profile NAME] --reset full     # snapshot, then full reset

Reset modes (scoped to the selected profile):
    soft  — delete the profile's SKILL.md; set refined_into_skill_<profile>=False
            on all matching docs; leave processed flags and batch notes untouched.
    full  — delete the profile's SKILL.md; delete batch_notes/; reset all docs to
            processed=False and refined_into_skill_<profile>=False; clear
            batch_notes_file and processed_date fields.

Dependencies:
    pyyaml
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from skill import HERE, load_profile, is_refined, set_refined
from corpus import load_state, save_state

ARCHIVE_DIR = HERE / "archive"
BATCH_NOTES_DIR = HERE / "batch_notes"
PROMPTS_DIR = HERE / "prompts"
STATE_FILE = HERE / "corpus_state.yaml"


def make_run_dir(profile_name: str, label: str) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    parts = [f"run_{stamp}", profile_name]
    if label:
        parts.append(label)
    run_dir = ARCHIVE_DIR / "_".join(parts)
    run_dir.mkdir(parents=True)
    return run_dir


def do_snapshot(run_dir: Path, skill_file: Path) -> None:
    copied = []

    # The profile's real built skill (e.g. skills/paper/SKILL.md). Flatten the
    # filename so several profiles' snapshots don't collide in one run dir.
    if skill_file.exists():
        dest_name = f"SKILL_{skill_file.parent.name}.md" if skill_file.name == "SKILL.md" else skill_file.name
        shutil.copy2(skill_file, run_dir / dest_name)
        copied.append(dest_name)

    if BATCH_NOTES_DIR.exists():
        shutil.copytree(BATCH_NOTES_DIR, run_dir / BATCH_NOTES_DIR.name)
        copied.append(f"{BATCH_NOTES_DIR.name}/")

    if PROMPTS_DIR.exists():
        shutil.copytree(PROMPTS_DIR, run_dir / PROMPTS_DIR.name)
        copied.append(f"{PROMPTS_DIR.name}/")

    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, run_dir / STATE_FILE.name)
        copied.append(STATE_FILE.name)

    if copied:
        print(f"Archived to: {run_dir}")
        for name in copied:
            print(f"  {name}")
    else:
        print(f"Archived to: {run_dir}  (nothing to copy — all sources absent)")


def _delete_skill(skill_file: Path) -> None:
    rel = skill_file.relative_to(HERE)
    if skill_file.exists():
        skill_file.unlink()
        print(f"Deleted {rel}")
    else:
        print(f"{rel} not found — skipping delete")


def do_reset_soft(profile) -> None:
    _delete_skill(profile.output)

    state = load_state()
    updated = 0
    for doc in state["documents"]:
        if profile.matches_type(doc) and is_refined(doc, profile):
            set_refined(doc, profile, False)
            doc.pop(f"refined_date_{profile.name}", None)
            updated += 1
    save_state(state)
    print(f"Reset {profile.refined_flag} on {updated} document(s) "
          f"(profile: {profile.name})")


def do_reset_full(profile) -> None:
    _delete_skill(profile.output)

    if BATCH_NOTES_DIR.exists():
        shutil.rmtree(BATCH_NOTES_DIR)
        print(f"Deleted {BATCH_NOTES_DIR.name}/")
    else:
        print(f"{BATCH_NOTES_DIR.name}/ not found — skipping delete")

    state = load_state()
    for doc in state["documents"]:
        doc["processed"] = False
        set_refined(doc, profile, False)
        doc["batch_notes_file"] = None
        doc.pop("processed_date", None)
        doc.pop(f"refined_date_{profile.name}", None)
    save_state(state)
    print(f"Reset {len(state['documents'])} document(s) to unprocessed state "
          f"(profile: {profile.name})")


def main():
    parser = argparse.ArgumentParser(
        description="Archive one profile's pipeline state and optionally reset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python archive.py
  python archive.py --profile paper --label before_refine
  python archive.py --reset soft
  python archive.py --reset full --label clean_slate
        """
    )
    parser.add_argument("--profile", metavar="NAME", default=None,
                        help="Profile from profiles.yaml (default: its default_profile)")
    parser.add_argument("--label", metavar="TEXT", default="",
                        help="Optional suffix appended to the archive folder name")
    parser.add_argument("--reset", choices=["soft", "full"],
                        help="Reset mode to apply after archiving (scoped to the profile)")
    args = parser.parse_args()

    profile = load_profile(args.profile)

    run_dir = make_run_dir(profile.name, args.label)
    do_snapshot(run_dir, profile.output)

    if args.reset == "soft":
        print()
        do_reset_soft(profile)
    elif args.reset == "full":
        print()
        do_reset_full(profile)


if __name__ == "__main__":
    main()
