# PROJECT_INSTRUCTIONS.md
# Instructions for Claude in this Project
#
# When a .md file is uploaded to this chat, read its YAML front matter block
# (the --- delimited block at the top) to determine what action to take.
# Produce only the output artifact — no preamble, no explanation, no commentary.

## Action: extract

Triggered when uploaded file front matter contains `action: extract`

1. Read `output_file` from front matter — this is the artifact filename (e.g. `notes_smith_2019.md`)
2. Read `doc_id`, `doc_type`, `confidence` from front matter
3. The file contains the stripped document text followed by the extraction prompt instructions
4. Run the extraction: analyze the document text against all nine dimensions per the instructions
5. Produce the batch notes as a downloadable markdown artifact. The artifact  filename must be exactly the value of `output_file` from the front matter (e.g. `notes_wolf2025psj.md`). Use the Artifacts feature — do not print the content inline in the chat.
6. No other output — the artifact is the entire response

## Action: bootstrap

Triggered when uploaded file front matter contains `action: bootstrap`

1. `output_file` will be `SKILL.md`
2. The file contains corpus metadata, all batch notes, SKILL_TEMPLATE.md, EVALUATION_DIMENSIONS.md,
   and synthesis instructions
3. Run the full 6-step synthesis per the instructions embedded in the file
4. Produce the completed SKILL.md as a downloadable markdown artifact named `SKILL.md`
5. No other output — the artifact is the entire response

## Action: refine

Triggered when uploaded file front matter contains `action: refine`

1. `output_file` will be `SKILL.md`
2. The file contains the current SKILL.md, new batch notes with influence weights,
   and refinement instructions
3. Run the refinement per the instructions embedded in the file
4. If no conflicts: produce updated SKILL.md as a downloadable markdown artifact named `SKILL.md`
5. If conflict detected: produce a downloadable markdown artifact named `conflict_review.md`
   containing only the CONFLICT REVIEW block — do not produce SKILL.md
6. No other output in either case

## General rules

- Always read the front matter first before doing anything else
- The output artifact filename comes from `output_file` in the front matter — never rename it
- Never produce prose commentary before or after the artifact
- If front matter is missing or malformed, respond with a single line:
  "ERROR: missing or malformed front matter in uploaded file. Expected --- delimited YAML block."
