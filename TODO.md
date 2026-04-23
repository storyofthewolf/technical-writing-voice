# TODO.md

## techncial
### evaluate to remove "Confidence" inteval weighting
### corpus.py registering cadence
    - add a preliminary token count to before extraction step
    - add token count to be shown under "Processed"
### add grouped extraction for small elements
    ```
    python extract.py --group wolf_research_statement barrier_letterofrec wolf_teaching_statement wolf_cover_letter
    ```
Behavior:
Reads each document's stripped text (extracting from PDF if needed)
Builds a single prompt file embedding all documents sequentially, each clearly delimited with its own header showing doc_id, doc_type, confidence, notes
Names the output prompt batch_notes/prompt_GROUP_docid1+docid2+....md
The front matter output_file should be notes_docid1+docid2+....md
The extraction prompt instructs Claude to produce one notes file covering all documents, with clearly labeled sections per document but a unified summary at the end


###In corpus.py, add --set-model DOC_ID MODEL_STRING command that writes an extraction_model field to the document entry in corpus_state.yaml. Same pattern as --set-confidence and --set-notes.
Also display it in the PROCESSED section of cmd_status() so you can see at a glance which model processed each document.


### Contaimination of existing "eric-wolf-voice" skill when creating the notes_{DOCID], about half the instances


## primary challenges
## tuning the prompt iterations. the prompts are structural and not as easy to evaluate and affect tuning outside of hand modifying
## evaluation of results is qualitative, motivating implementation of tuning elements to shape voice
## token consumption is high
    - I have had to iterate on the prompt sequences with Gemini Pro, and test on Gemini Pro using the Skill file as system_prompt
    - Testing SKILL in Claude is probably doable, but batch prompt iteration will be token expensive

## qualitative critiques for outcomes from A/B tests
    - Gemini Pro: used "Note that" to begin each of the three
    - overuse of adverbs
    - some incorrect science terminology crept into the responses
  

  

