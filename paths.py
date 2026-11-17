#!/usr/bin/env python

"""
paths.py
--------
Resolves which corpus a command operates on, and where that corpus keeps its
working data. Shared by corpus.py, extract.py, skill.py, archive.py, and
overrides.py.

Each author's corpus is a self-contained workspace under corpora/<name>/:

    corpora/<name>/
        corpus_state.yaml   registered documents and their processing state
        overrides.yaml      manual overrides for this corpus's skills
        batch_notes/        extraction notes (notes_{doc}.md or notes_batch_*.md)
        stripped_text/      plain text stripped from each source document
        prompts/            assembled synthesis / refinement / revision prompts
        archive/            archive.py snapshots
        validation/         held-out validation briefs, drafts, comparisons

corpora/ is gitignored in full: corpus data never leaves the machine.

Configuration comes from profiles.yaml (tracked) merged with
profiles.local.yaml (gitignored, optional). The local file holds corpora and
profiles that must stay off GitHub, such as another author's voice. Entries
in the local file are added to, or replace, same-named entries in the tracked
file.

Selecting a corpus on the command line:
    --corpus NAME     use this corpus directly
    --profile NAME    use the corpus that profile is built from
    (neither)         use the corpus of profiles.yaml's default_profile
"""

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
PROFILES_FILE = HERE / "profiles.yaml"
LOCAL_PROFILES_FILE = HERE / "profiles.local.yaml"

DEFAULT_DIMENSIONS = "core/EVALUATION_DIMENSIONS.md"
DEFAULT_EXTRACTION_TEMPLATE = "templates/extraction_prompt.md"
EXTRACTION_MODES = ("per_document", "batch")


def _die(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_config() -> dict:
    """profiles.yaml merged with profiles.local.yaml. profiles.yaml is required."""
    if not PROFILES_FILE.exists():
        _die("profiles.yaml not found. It defines the corpora and skill "
             "profiles and is required.")
    with open(PROFILES_FILE) as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("corpora", {})
    cfg.setdefault("profiles", {})
    if LOCAL_PROFILES_FILE.exists():
        with open(LOCAL_PROFILES_FILE) as f:
            local = yaml.safe_load(f) or {}
        cfg["corpora"].update(local.get("corpora") or {})
        cfg["profiles"].update(local.get("profiles") or {})
        if local.get("default_profile"):
            cfg["default_profile"] = local["default_profile"]
    return cfg


class Corpus:
    """One author's corpus workspace and its domain settings."""

    def __init__(self, name: str, data: dict):
        self.name = name
        self.root = HERE / data.get("root", f"corpora/{name}")
        self.description = (data.get("description") or "").strip()
        self.doc_types = list(data.get("doc_types") or ["other"])
        if "other" not in self.doc_types:
            self.doc_types.append("other")
        self.default_type_for_suffix = data.get("default_type_for_suffix") or {}
        self.dimensions_file = HERE / data.get("dimensions", DEFAULT_DIMENSIONS)
        self.extraction_template = HERE / data.get(
            "extraction_template", DEFAULT_EXTRACTION_TEMPLATE)
        self.extraction_mode = data.get("extraction_mode", "per_document")
        if self.extraction_mode not in EXTRACTION_MODES:
            _die(f"corpus '{name}': extraction_mode must be one of "
                 f"{', '.join(EXTRACTION_MODES)}")

    # Working-data locations -------------------------------------------------
    @property
    def state_file(self) -> Path:
        return self.root / "corpus_state.yaml"

    @property
    def overrides_file(self) -> Path:
        return self.root / "overrides.yaml"

    @property
    def batch_notes_dir(self) -> Path:
        return self.root / "batch_notes"

    @property
    def stripped_text_dir(self) -> Path:
        return self.root / "stripped_text"

    @property
    def prompts_dir(self) -> Path:
        return self.root / "prompts"

    @property
    def archive_dir(self) -> Path:
        return self.root / "archive"

    @property
    def validation_dir(self) -> Path:
        return self.root / "validation"

    def resolve(self, stored: str | None) -> Path | None:
        """Resolve a path stored in corpus_state.yaml. Stored paths are relative
        to the corpus root; absolute paths are honored as-is."""
        if not stored:
            return None
        p = Path(stored)
        return p if p.is_absolute() else self.root / p

    def relative(self, path: Path) -> str:
        """Express a path inside the corpus root as a root-relative string."""
        try:
            return str(Path(path).relative_to(self.root))
        except ValueError:
            return str(path)


def resolve_profile_name(cfg: dict, profile: str | None) -> str:
    chosen = profile or cfg.get("default_profile")
    if not chosen:
        _die("no --profile given and no default_profile in profiles.yaml.")
    if chosen not in cfg["profiles"]:
        _die(f"profile '{chosen}' not found. Available: "
             f"{', '.join(sorted(cfg['profiles']))}")
    return chosen


def load_corpus(corpus: str | None = None, profile: str | None = None) -> Corpus:
    """Resolve a corpus by name, by profile, or via the default profile."""
    cfg = load_config()
    if corpus is None:
        pname = resolve_profile_name(cfg, profile)
        corpus = cfg["profiles"][pname].get("corpus")
        if not corpus:
            _die(f"profile '{pname}' does not name a corpus.")
    if corpus not in cfg["corpora"]:
        _die(f"corpus '{corpus}' not found. Available: "
             f"{', '.join(sorted(cfg['corpora']))}")
    return Corpus(corpus, cfg["corpora"][corpus])


def add_selector_args(parser) -> None:
    """Add the shared --corpus / --profile selectors to an argparse parser."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--corpus", metavar="NAME", default=None,
                       help="Corpus from profiles.yaml (default: the default "
                            "profile's corpus)")
    group.add_argument("--profile", metavar="NAME", default=None,
                       help="Select the corpus this profile is built from")


def read_yaml(path: Path, default):
    if not path.exists():
        return default
    with open(path) as f:
        data = yaml.safe_load(f)
    return default if data is None else data


def write_yaml(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False)
