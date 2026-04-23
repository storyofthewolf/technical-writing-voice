#!/usr/bin/env python

"""
overrides.py
------------
Manage manual overrides for voice refinement. Overrides are stored in
overrides.yaml at the project root and injected into every prompt generated
by refine.py.

Usage:
    python overrides.py list
    python overrides.py add "Always spell out numbers below ten."
    python overrides.py add --category syntax "Prefer active voice in methods."
    python overrides.py remove OVERRIDE_ID
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

OVERRIDES_FILE = Path(__file__).parent / "overrides.yaml"


def load_overrides() -> list:
    if not OVERRIDES_FILE.exists():
        return []
    with open(OVERRIDES_FILE) as f:
        data = yaml.safe_load(f) or []
    return data if isinstance(data, list) else []


def save_overrides(overrides: list) -> None:
    with open(OVERRIDES_FILE, "w") as f:
        yaml.dump(overrides, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _next_id(overrides: list) -> str:
    existing = {o["id"] for o in overrides}
    n = 1
    while True:
        candidate = f"ov{n:03d}"
        if candidate not in existing:
            return candidate
        n += 1


def cmd_list(overrides: list) -> None:
    if not overrides:
        print("No overrides defined.")
        print("Add one with: python overrides.py add \"TEXT\"")
        return
    print(f"{'ID':<8} {'CATEGORY':<16} {'ADDED':<12} INSTRUCTION")
    print(f"{'-'*8} {'-'*16} {'-'*12} {'-'*40}")
    for o in overrides:
        category = o.get("category") or ""
        print(f"{o['id']:<8} {category:<16} {o.get('added', ''):<12} {o['instruction']}")


def cmd_add(text: str, category: str, overrides: list) -> None:
    text = text.strip()
    if not text:
        print("ERROR: instruction text cannot be empty.")
        sys.exit(1)
    entry = {
        "id": _next_id(overrides),
        "instruction": text,
        "added": datetime.now().strftime("%Y-%m-%d"),
    }
    if category:
        entry["category"] = category.strip()
    overrides.append(entry)
    save_overrides(overrides)
    print(f"Added override {entry['id']}: {text}")


def cmd_remove(override_id: str, overrides: list) -> None:
    before = len(overrides)
    remaining = [o for o in overrides if o["id"] != override_id]
    if len(remaining) == before:
        print(f"ERROR: Override ID not found: '{override_id}'")
        print("Run 'python overrides.py list' to see existing IDs.")
        sys.exit(1)
    save_overrides(remaining)
    print(f"Removed override {override_id}.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage manual voice overrides.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python overrides.py list
  python overrides.py add "Always spell out numbers below ten."
  python overrides.py add --category syntax "Prefer active voice."
  python overrides.py remove ov001
        """
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all overrides")

    add_p = sub.add_parser("add", help="Add a new override")
    add_p.add_argument("text", metavar="TEXT", help="Override instruction text")
    add_p.add_argument("--category", metavar="CAT", default="",
                       help="Optional category label (e.g. syntax, tone)")

    rem_p = sub.add_parser("remove", help="Remove an override by ID")
    rem_p.add_argument("id", metavar="ID", help="Override ID to remove")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    overrides = load_overrides()

    if args.command == "list":
        cmd_list(overrides)
    elif args.command == "add":
        cmd_add(args.text, args.category, overrides)
    elif args.command == "remove":
        cmd_remove(args.id, overrides)


if __name__ == "__main__":
    main()
