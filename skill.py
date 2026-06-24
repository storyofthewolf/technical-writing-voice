#!/usr/bin/env python

"""
skill.py
--------
Builds and maintains purpose-specific SKILL.md profiles from corpus batch notes.

Profiles are defined in profiles.yaml (required). Each profile is a narrow voice
skill aimed at one writing context (e.g. `paper`). The selected profile
determines which document types feed synthesis, which synthesis instructions are
used, where the built skill is written, and how the skill handles LaTeX/.bib
markup.

Usage:
    python skill.py [--profile NAME] --bootstrap
        First-time synthesis prompt from the profile's processed notes.
        Paste output into Claude → save response → run --apply.

    python skill.py [--profile NAME] --refine FILE
        Refinement prompt comparing a notes file against the profile's SKILL.md.

    python skill.py [--profile NAME] --refine --all
        Refinement prompt bundling all of the profile's unrefined notes.

    python skill.py [--profile NAME] --revision FILE
        Revision prompt from a freeform instructions file (authoritative).

    python skill.py [--profile NAME] --apply CLAUDE_RESPONSE
        Apply Claude's response to the profile's SKILL.md (conflict-checks first).

    python skill.py [--profile NAME] --overrides
        Append or replace the ## Manual Overrides section in the profile's SKILL.md.

    python skill.py --output FILE
        Write prompt to FILE instead of the default prompts/ path.

    --profile defaults to profiles.yaml `default_profile`.

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
PROFILES_FILE = HERE / "profiles.yaml"
REFINEMENT_PROMPT_FILE = HERE / "templates" / "refinement_prompt.md"
REVISION_PROMPT_FILE = HERE / "templates" / "revision_prompt.md"
EVALUATION_DIMENSIONS_FILE = HERE / "core" / "EVALUATION_DIMENSIONS.md"

# General fallback skill-output template, used by any profile that does not set
# its own `skill_template` and is not the slim `paper` profile.
GENERAL_SKILL_TEMPLATE_FILE = HERE / "core" / "SKILL_TEMPLATE.md"


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

class Profile:
    """Resolved settings for one purpose-specific skill build."""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.skill_name = data.get("skill_name", f"{name}-voice")
        self.purpose = (data.get("purpose") or "").strip()
        self.corpus_types = data.get("corpus_types")  # None = all types
        self.target_tokens = data.get("target_tokens")
        self.latex_policy = data.get("latex_policy", "defer")
        self.output = HERE / data.get("output", "SKILL.md")
        self.synthesis_template = HERE / data.get(
            "synthesis_template", "templates/synthesis_prompt.md"
        )
        # Slim paper template if it exists, else the general template.
        skill_tmpl = data.get("skill_template")
        if skill_tmpl:
            self.skill_template = HERE / skill_tmpl
        elif (HERE / "core" / "SKILL_TEMPLATE_PAPER.md").exists() and name == "paper":
            self.skill_template = HERE / "core" / "SKILL_TEMPLATE_PAPER.md"
        else:
            self.skill_template = GENERAL_SKILL_TEMPLATE_FILE

    @property
    def refined_flag(self) -> str:
        """Per-profile incorporation flag in corpus_state.yaml."""
        return f"refined_into_skill_{self.name}"

    def matches_type(self, doc: dict) -> bool:
        if not self.corpus_types:
            return True
        return doc.get("type") in self.corpus_types


def load_profile(name: str | None) -> Profile:
    if not PROFILES_FILE.exists():
        print("ERROR: profiles.yaml not found. It defines the available skill "
              "profiles and is required.")
        sys.exit(1)

    with open(PROFILES_FILE) as f:
        cfg = yaml.safe_load(f) or {}
    profiles = cfg.get("profiles", {})
    if not profiles:
        print("ERROR: profiles.yaml defines no profiles.")
        sys.exit(1)

    chosen = name or cfg.get("default_profile")
    if not chosen:
        print("ERROR: no --profile given and no default_profile in profiles.yaml.")
        sys.exit(1)
    if chosen not in profiles:
        print(f"ERROR: profile '{chosen}' not found in profiles.yaml. "
              f"Available: {', '.join(sorted(profiles))}")
        sys.exit(1)

    return Profile(chosen, profiles[chosen])


def is_refined(doc: dict, profile: Profile) -> bool:
    return bool(doc.get(profile.refined_flag))


def set_refined(doc: dict, profile: Profile, value: bool) -> None:
    doc[profile.refined_flag] = value
    doc[f"refined_date_{profile.name}"] = datetime.now().strftime("%Y-%m-%d")


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
# Corpus stats
# ---------------------------------------------------------------------------
# Documents contribute evenly to synthesis. Token counts are reported as
# informational corpus-size metadata only — they carry no weight. Claude weighs
# patterns by how consistently they recur across the per-document notes, not by
# any token or confidence arithmetic.

def compute_corpus_stats(state: dict, profile: Profile = None) -> dict:
    processed = [d for d in state["documents"] if d.get("processed")]
    if profile is not None:
        processed = [d for d in processed if profile.matches_type(d)]
    raw_tokens = sum(d.get("prose_tokens", 0) for d in processed)
    return {
        "doc_count": len(processed),
        "raw_tokens": raw_tokens,
        "processed_docs": processed,
    }


# ---------------------------------------------------------------------------
# Collect unrefined notes
# ---------------------------------------------------------------------------

def get_unrefined_notes(state: dict, profile: Profile) -> list[dict]:
    return [
        d for d in state["documents"]
        if d.get("processed")
        and profile.matches_type(d)
        and not is_refined(d, profile)
    ]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _profile_directives_block(profile: Profile) -> str:
    """Profile settings injected at the top of the bootstrap prompt so Claude
    knows the skill name, purpose, length budget, and LaTeX policy."""
    budget = (f"{profile.target_tokens:,} tokens" if profile.target_tokens
              else "no hard limit (keep it tight)")
    types = ", ".join(profile.corpus_types) if profile.corpus_types else "all types"
    latex = {
        "defer": "DEFER all LaTeX/.bib/figure markup to Claude's standard best "
                 "practices. Do NOT prescribe markup conventions in the skill — "
                 "it governs prose voice and argument structure only.",
    }.get(profile.latex_policy, profile.latex_policy)
    return f"""## Profile directives (honor these exactly)

- **Profile:** {profile.name}
- **Skill name (front matter `name`):** {profile.skill_name}
- **Purpose:** {profile.purpose}
- **Source corpus types:** {types}
- **Token budget:** {budget}
- **LaTeX policy:** {latex}
"""


def build_bootstrap_prompt(state: dict, profile: Profile) -> str:
    synthesis_prompt = load_file(profile.synthesis_template,
                                 profile.synthesis_template.name)
    skill_template = load_file(profile.skill_template, profile.skill_template.name)
    eval_dims = load_file(EVALUATION_DIMENSIONS_FILE, "EVALUATION_DIMENSIONS.md")
    corpus_stats = compute_corpus_stats(state, profile)

    if not corpus_stats["processed_docs"]:
        types = ", ".join(profile.corpus_types) if profile.corpus_types else "any"
        print(f"ERROR: no processed documents of type [{types}] for profile "
              f"'{profile.name}'. Register/extract matching documents first.")
        sys.exit(1)

    notes_block = ""
    for doc in corpus_stats["processed_docs"]:
        notes_file = doc.get("batch_notes_file")
        if notes_file and Path(notes_file).exists():
            notes_content = Path(notes_file).read_text(encoding="utf-8")
            notes_block += f"\n\n---\n## Batch notes: {doc['id']} ({doc.get('type')})\n\n{notes_content}"
        else:
            notes_block += f"\n\n---\n## Batch notes: {doc['id']}\n[Notes file not found: {notes_file}]"

    metadata_block = f"""## Corpus metadata (for SKILL.md header)

- Documents processed: {corpus_stats['doc_count']}
- Raw prose tokens: {corpus_stats['raw_tokens']:,}  (informational corpus size; not a weight)
- Analysis date: {datetime.now().strftime("%Y-%m")}

All documents contribute evenly. Weigh a pattern by how consistently it recurs
across the per-document notes below, not by token count.
"""

    return f"""---
action: bootstrap
profile: {profile.name}
output_file: {profile.output.relative_to(HERE)}
generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
---

{_profile_directives_block(profile)}

---

{metadata_block}

---

## Batch notes ({profile.name} corpus)
{notes_block}

---

## EVALUATION_DIMENSIONS.md (reference)

{eval_dims}

---

## {profile.skill_template.name} (output format)

{skill_template}

---

## Synthesis instructions

{synthesis_prompt}
"""


def build_refinement_prompt(new_notes_docs: list[dict], state: dict, profile: Profile) -> str:
    refinement_prompt_template = load_file(REFINEMENT_PROMPT_FILE, "refinement_prompt.md")
    current_skill = load_file(profile.output, str(profile.output.name))
    corpus_stats = compute_corpus_stats(state, profile)

    new_notes_block = ""
    new_count = len(new_notes_docs)
    prior_count = corpus_stats["doc_count"]

    for doc in new_notes_docs:
        notes_file = doc.get("batch_notes_file")
        if notes_file and Path(notes_file).exists():
            notes_content = Path(notes_file).read_text(encoding="utf-8")
        else:
            notes_content = f"[Notes file not found: {notes_file}]"

        new_notes_block += f"""
---
## New batch notes: {doc['id']}
**Document type:** {doc['type']}
**Prose tokens:** {doc.get('prose_tokens', 0):,}  (informational; not a weight)

{notes_content}
"""

    corpus_summary = f"""## Corpus context

Documents already incorporated into the current SKILL.md: {prior_count}
New document(s) in this refinement: {new_count}

All documents contribute evenly. The current SKILL.md already reflects
{prior_count} document(s); these {new_count} new document(s) are a smaller share
of the combined evidence. Do not let a pattern that appears in only the new
notes overturn one established across the prior corpus unless it recurs
consistently — weigh by how often a pattern is observed across documents, never
by token count.
"""

    return f"""---
action: refine
profile: {profile.name}
output_file: {profile.output.relative_to(HERE)}
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


def build_revision_prompt(instructions: str, profile: Profile) -> str:
    revision_prompt_template = load_file(REVISION_PROMPT_FILE, "revision_prompt.md")
    current_skill = load_file(profile.output, str(profile.output.name))

    return f"""---
action: revision
profile: {profile.name}
output_file: {profile.output.relative_to(HERE)}
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

def _inject_overrides(text: str, overrides_block: str) -> str:
    marker = "## Manual Overrides"
    if marker in text:
        return re.sub(
            r"## Manual Overrides\b.*",
            overrides_block,
            text,
            count=1,
            flags=re.DOTALL,
        )
    if overrides_block:
        return text.rstrip("\n") + "\n\n---\n\n" + overrides_block + "\n"
    return text


def cmd_apply(response_file: str, state: dict, profile: Profile) -> None:
    response_path = Path(response_file)
    if not response_path.exists():
        print(f"ERROR: Response file not found: {response_path}")
        sys.exit(1)

    response_text = response_path.read_text(encoding="utf-8")

    if detect_conflict(response_text):
        print_conflict(response_text)
        print(f"\n{profile.output.name} was NOT updated. Resolve the conflict first.")
        return

    response_text = _inject_overrides(response_text, _overrides_block(load_overrides()))

    profile.output.parent.mkdir(parents=True, exist_ok=True)
    profile.output.write_text(response_text, encoding="utf-8")
    print(f"{profile.output.relative_to(HERE)} updated (profile: {profile.name}).")

    # Mark this profile's unrefined matching docs as incorporated.
    updated = 0
    for doc in state["documents"]:
        if (doc.get("processed") and profile.matches_type(doc)
                and not is_refined(doc, profile)):
            set_refined(doc, profile, True)
            updated += 1

    if updated:
        from corpus import save_state
        save_state(state)
        print(f"Marked {updated} document(s) as incorporated into "
              f"{profile.output.name} (profile: {profile.name}).")


def cmd_overrides(profile: Profile) -> None:
    if not profile.output.exists():
        print(f"ERROR: {profile.output.relative_to(HERE)} not found. Run --bootstrap first.")
        sys.exit(1)

    overrides = load_overrides()
    if not overrides:
        print("No overrides found in overrides.yaml — nothing to do.")
        return

    skill_text = profile.output.read_text(encoding="utf-8")
    skill_text = _inject_overrides(skill_text, _overrides_block(overrides))
    profile.output.write_text(skill_text, encoding="utf-8")
    print(f"{profile.output.relative_to(HERE)} updated with {len(overrides)} override(s).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build and maintain purpose-specific SKILL.md profiles from corpus batch notes."
    )
    parser.add_argument("--profile", metavar="NAME", default=None,
                        help="Profile from profiles.yaml (default: its default_profile)")
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

    profile = load_profile(args.profile)

    if args.overrides:
        cmd_overrides(profile)
        return

    state = load_state()

    if args.apply:
        cmd_apply(args.apply, state, profile)
        return

    datestamp = datetime.now().strftime("%Y-%m-%d")
    new_docs = []

    if args.bootstrap:
        prompt = build_bootstrap_prompt(state, profile)

    elif args.revision:
        revision_path = Path(args.revision)
        if not revision_path.exists():
            print(f"ERROR: Instructions file not found: {revision_path}")
            sys.exit(1)
        if not profile.output.exists():
            print(f"No {profile.output.name} found for profile '{profile.name}'. "
                  "Run --bootstrap first.")
            sys.exit(1)
        instructions = revision_path.read_text(encoding="utf-8")
        prompt = build_revision_prompt(instructions, profile)

    elif args.refine is not None:
        if args.all or args.refine == "--all":
            # Bundle all unrefined notes for this profile
            unrefined = get_unrefined_notes(state, profile)
            if not unrefined:
                print(f"No unrefined batch notes for profile '{profile.name}'.")
                print(f"All matching documents are incorporated into {profile.output.name}.")
                print("To add new documents: python corpus.py --add <path>")
                return
            if not profile.output.exists():
                print(f"No {profile.output.name} found. Run --bootstrap for first-time synthesis.")
                return
            new_docs = unrefined
            prompt = build_refinement_prompt(unrefined, state, profile)
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
            off_type = [d for d in matching if not profile.matches_type(d)]
            if off_type:
                print(f"WARNING: {notes_file} is type '{off_type[0].get('type')}', "
                      f"not in profile '{profile.name}' corpus_types "
                      f"({profile.corpus_types}). Refining anyway as instructed.")
            new_docs = matching
            prompt = build_refinement_prompt(matching, state, profile)

    else:
        parser.print_help()
        return

    PROMPTS_DIR = HERE / "prompts"
    PROMPTS_DIR.mkdir(exist_ok=True)

    if args.output:
        out_path = Path(args.output)
    elif args.bootstrap:
        out_path = PROMPTS_DIR / f"bootstrap_prompt_{profile.name}_{datestamp}.md"
    elif args.revision:
        out_path = PROMPTS_DIR / f"revision_prompt_{profile.name}_{datestamp}.md"
    else:
        doc_slug = "+".join(d["id"] for d in new_docs)
        out_path = PROMPTS_DIR / f"refinement_prompt_{profile.name}_{doc_slug}_{datestamp}.md"

    out_path.write_text(prompt, encoding="utf-8")
    print(f"Prompt written to: {out_path}")
    print(f"Upload {out_path.name} to Claude → save response → run: python skill.py --apply <response_file>")


if __name__ == "__main__":
    main()
