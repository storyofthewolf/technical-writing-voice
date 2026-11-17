# synthesis_advocacy.md

Synthesis instructions for an association advocacy / government-relations
voice profile. `skill.py --bootstrap` embeds everything below the line into
the bootstrap prompt, after the profile directives, corpus metadata, batch
notes, the rubric, and the output template. You do not fill this in by hand.

How this differs from the paper template:

1. **The skill is used for more genres than it learned from.** The corpus may
   cover only one or two genres (for example a member column), while the skill
   is used for memos, press releases, blog posts, columns, and member emails.
   The skill carries the sentence-level voice across and leaves genre layout to
   standard conventions.
2. **Recurrence over a small corpus.** Documents are short. Batch notes report
   recurrence as "N of M documents". Use those counts directly.
3. **Format, not markup.** There is no LaTeX. The profile's format policy says
   how much genre layout the skill may prescribe.

---

You are synthesizing voice observations into a slim SKILL.md for **one writer
who writes on behalf of an association for its members**: government-relations
updates, columns, memos, press releases, blog posts. The skill is loaded by
Claude when drafting or revising any of these on the writer's behalf.

## Your inputs

The prompt above contains:

- **Profile directives**: skill name, writer name (if given), purpose, source
  document types, token budget, and format policy. Honor them exactly.
- **Corpus metadata**: document count and token count (informational only).
- **Batch notes**: observations per dimension with quoted evidence and
  recurrence counts. A batch file may cover several documents at once.
- **The rubric** (the evaluation dimensions for this domain), for reference.
- **The output template**, the exact format to produce.

## Scope discipline

- **Prose voice and argument shape only.** Sentence habits, word choice,
  stance, how pieces open, argue, report numbers, ask for action, and close.
- **Genre layout follows convention.** Do not prescribe press-release
  datelines, memo header blocks, or boilerplate. Claude knows those. Describe
  only layout choices the corpus shows the writer making by choice, and only
  where they would carry over.
- **Separate the writer from the format.** A column's standing title, its
  recurring results table, or a fixed sign-off are format conventions. Leave
  them out of the voice description unless the notes show the habit outside
  that format, or the profile's purpose names that format as a target.
- **No invented registers.** If the corpus is one genre, say so in the
  instruction block and do not invent how the writer sounds in a press release.
  The template's genre notes tell Claude how to carry the voice over.

## Your task

Work through these steps in order. Do not emit the SKILL.md until all are done.

### Step 1: Audit the notes

Read every notes section. For each observation, record its recurrence count.
Collect the "Format conventions" and "Flags for synthesis" entries.

### Step 2: Resolve observations per dimension

- **Core patterns** recur in at least half the documents. These form the skill.
- **Secondary patterns** recur in a meaningful minority (roughly a quarter or
  more). Include them briefly if they are distinctive.
- **Single-document observations** are dropped unless striking, and never
  stated as habits.
- **Generic** observations (what any association communicator does) are cut.
- **Format conventions** are cut from the dimensions (see scope discipline).

All documents contribute evenly. Judge strength by recurrence and consistency,
never by length.

### Step 3: Rank dimensions and cut hard

Rank by recurrence × consistency × distinctiveness. Only HIGH and the
strongest MEDIUM dimensions get full sections. Weak ones go in one short
"Lesser patterns" note or are omitted. A reader who stops after the top three
dimensions should already have a usable voice.

### Step 4: Write the genre carry-over notes

For each target genre named in the profile's purpose (for example memo, press
release, blog post, column, member email), write one or two lines: which of
the core patterns carry over unchanged, which soften, and which drop. Ground
this in the evidence. Where the corpus shows nothing about a genre, say that
the voice's sentence-level habits apply inside the genre's standard layout.

If the notes describe an attributed-quote (spokesperson) sub-register, record
it in the press-release line.

### Step 5: Write the voice characterization

Write this last. 4 to 6 sentences, a portrait not a checklist, anchored in the
2 or 3 most distinctive core patterns, naming the writer's role and audience.
It must be specific enough that it would not describe another association's
GR writer.

### Step 6: Produce the completed SKILL.md

Using the output template as the exact format:

- Output the complete SKILL.md, ready to save.
- Remove all HTML comment blocks.
- Front matter: `name` is the profile's skill name. `description` follows the
  template, filling in the writer's name (or "the author" if no name is given),
  role, and association type. Do not name the association unless the profile
  directives do.
- Keep the "Instructions for Claude" block as written in the template, filling
  in the bracketed fields. It must come immediately after the front matter.
- Order dimension sections by rank, highest first.
- **Do not copy verbatim quotes from the corpus into the skill.** Describe the
  pattern. Short fragments you write yourself to illustrate a pattern are fine.
  Lifted corpus sentences are not, because the model will overuse them.
- **Do not prescribe punctuation** (em dashes, colons, semicolons, exclamation
  points) unless the notes show a clear recurring habit with counts.
- Honor the token budget. If over, cut MEDIUM/LOW content first.
- Fill the corpus metadata block and the synthesis notes briefly.

## Output

Write only the completed SKILL.md content: no preamble, no commentary.
