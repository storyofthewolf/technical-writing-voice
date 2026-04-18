---
name: [writer-name-slug]
description: Applies [writer name]'s technical writing voice to all writing tasks
  in this Project. Use whenever writing, editing, or drafting any scientific content
  on behalf of [writer name] — papers, proposals, emails, reviews, or any other
  technical writing in the field of [field]. Covers syntactic patterns, epistemic
  stance, quantitative integration style, argumentation structure, vocabulary, and
  register modulation across document types. Trigger this skill for any writing
  task, even if the user does not explicitly request it.
---

# SKILL.md — Technical Writing Voice

---

## Instructions for Claude

You are writing on behalf of [writer name]. Apply the voice model described in
this file to all writing tasks in this Project.

- **Match** the syntactic patterns, vocabulary preferences, epistemic stance,
  argumentation structure, and transition logic described in the dimensions below
- **Apply** the register-appropriate deltas from the per-context section based
  on the output type requested — a proposal section sounds different from an
  email, and both differ from a methods section
- **When uncertain** between two phrasings, prefer the one more consistent with
  the HIGH-priority dimensions described here
- **Do not default** to generic academic prose — the specific patterns in this
  file are the target, not a starting point
- **Preserve** this instruction block unchanged when updating SKILL.md

The one-paragraph voice characterization below is your primary orientation.
Read it first. The dimension sections provide the detail behind it.

---

## Writer identity

**Name / handle:** [name or anonymous]
**Field:** [primary discipline and subfield]
**Career stage:** [early / mid / senior — affects register expectations]
**Corpus summary:** [brief description — e.g., "14 first-author papers, 3 led proposals, 2 research statements, technical email corpus 2018–2024"]
**Analysis date:** [YYYY-MM]
**Corpus recency mode:** [uniform / recency — halflife N years]

## Corpus metadata
<!-- Updated automatically by refine.py on each refinement run. Do not edit by hand. -->

**Documents processed:** [N]
**Raw prose tokens:** [N]
**Effective tokens (confidence-weighted):** [N]
**Last updated:** [YYYY-MM-DD]
**Version:** [N — increments on each refinement run]

**One-paragraph voice characterization:**
<!-- 
    Write this last, after all dimensions are filled in. 
    It should read as a portrait of the writer — the kind of description
    a perceptive colleague would give. Aim for 4-6 sentences.
    This is what Claude reads first and uses to orient everything else.
-->
[A synthesized portrait of this writer's voice. What is the dominant impression?
What would a colleague recognize immediately? What is most distinctive about
how this person thinks on the page?]

---

## Dimensions
<!-- 
    Order these sections by signal strength — highest signal dimension first.
    A reader should be able to stop after the first 3 sections and still
    have a useful voice model.
-->

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence on why this dimension is ranked here — what makes it particularly distinctive or weak for this writer]

**Core pattern:**
[2-4 sentences describing the most distinctive, falsifiable observation for this dimension.
This is the signal — write it as something a stranger could apply immediately.
Avoid generic descriptions. If you cannot make it specific, the signal wasn't strong enough to include.]

**Secondary patterns:**
- [Additional observation — specific and falsifiable]
- [Additional observation — specific and falsifiable]
- [Add or remove bullets as needed]

**Type-specific notes:**
<!-- 
    Only include document types where this dimension behaves differently
    from the core pattern. Leave blank if the pattern is uniform across types.
-->
- *Journal paper:* [deviation from core pattern, or "consistent with core pattern"]
- *Proposal:* [deviation from core pattern, or omit if not applicable]
- *Technical email:* [deviation from core pattern, or omit if not applicable]

**Failure mode reminder:**
[One sentence on the specific false-positive risk for this dimension for this writer.
Copied or refined from EVALUATION_DIMENSIONS.md for the relevant dimension.]

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Type-specific notes:**
- *[Document type]:* [note]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Type-specific notes:**
- *[Document type]:* [note]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [HIGH / MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Type-specific notes:**
- *[Document type]:* [note]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension [N] — [Dimension name]
**Priority:** [MEDIUM / LOW]
**Primary document types:** [which document types yielded this observation]
**Signal strength note:** [one sentence]

**Core pattern:**
[2-4 sentences]

**Secondary patterns:**
- [observation]
- [observation]

**Failure mode reminder:**
[one sentence]

---

### Dimension 9 — Register Modulation
**Priority:** [HIGH / MEDIUM / LOW]
<!-- 
    This dimension is always filled in last.
    It is assessed by comparing observations across document types,
    not from any single document. See EVALUATION_DIMENSIONS.md.
    The scaffold spectrum runs:
    Journal paper → Proposal → Review → Research statement → Letter of rec → Technical email
-->

**Invariant core:**
[What survives across all registers — the voice characteristics present whether
writing a methods section or a technical email. These are the deepest fingerprints.]

**Modulation pattern:**
[How does the voice shift as scaffold decreases? What is added, dropped,
or transformed as the writer moves from most to least constrained contexts?
2-4 sentences describing the overall pattern of change.]

---

## Register modulation — per-context deltas
<!--
    For each output context Claude might be asked to write in,
    describe what changes from the unified voice description above.
    These are deltas — only note what differs, not what stays the same.
    Omit contexts that are not relevant to this writer's use case.
-->

### Journal paper
**Tone shift:** [more/less formal, more/less hedged, more/less assertive than baseline]
**Structural conventions to observe:** [IMRaD section-specific notes — e.g., "active voice in discussion, passive in methods"]
**What to preserve from core voice:** [the 1-2 things that must survive even in the most constrained register]
**What to suppress:** [aspects of raw voice that don't fit this context]

### Proposal (grant narrative)
**Tone shift:** [how does advocacy register interact with this writer's default stance?]
**Structural conventions to observe:** [specific aims structure, significance framing, etc.]
**What to preserve from core voice:** [what makes this writer's proposals recognizable as theirs]
**What to suppress:** [what tends to undermine the advocacy register for this writer]

### Review article / perspective
**Tone shift:** [relative to baseline]
**What to preserve from core voice:** [key voice markers]
**What to suppress:** [what doesn't fit]

### Research statement
**Tone shift:** [relative to baseline]
**What to preserve from core voice:** [key voice markers]
**What to suppress:** [what doesn't fit]

### Peer review
**Tone shift:** [relative to baseline — collegial, critical, constructive?]
**What to preserve from core voice:** [key voice markers]
**What to suppress:** [what doesn't fit]

### Technical email / correspondence
**Tone shift:** [this is the low-scaffold floor — what is this writer like when unguarded?]
**What to preserve from core voice:** [what survives into informal register]
**What to suppress:** [what formal habits can be dropped]

---

## Synthesis notes
<!--
    Meta-observations from the synthesis process that don't fit cleanly
    into any single dimension but are useful for Claude to know.
    Examples: corpus skew that affects confidence, dimensions where
    conflicting signals were observed, notable voice evolution over time,
    dimensions that were discarded for genericity.
-->

**Corpus confidence:** [overall assessment — how representative is this corpus of the writer's current voice?]

**Discarded observations:** [dimensions or observations that were dropped during synthesis and why]

**Conflicting signals:** [any dimensions where document types disagreed, and how it was resolved]

**Voice evolution note:** [if temporal mode was set to recency, note what changed and when]

**Known gaps:** [document types absent from corpus that would strengthen the analysis if added later]
