# Reference-material manifest specification (for the Gemini procedure; specification only, nothing built)

The custodian builds the manifest at Holdout #2 build time, before any transmission, and its SHA-256 is recorded in the ledger. It contains one record per reserve item and one record per clip reference set, and only these fields:
- clip_code (pseudonymous code, not a title or source name);
- reference_A_file_sha256 and reference_B_file_sha256 (the two reference images, labelled only "Target A" and "Target B");
- item_id (blinded), item_image_sha256, item order position (ascending item_id as in the blinded sheet);
- request_template_id = hash of PROMPT_V1.txt.

The manifest MUST NOT contain: wrestler, promotion, event or source names; file names that reveal them; the item-to-tracklet map; first-pass labels; truth class; model or B0 output; results; reserve-selection seed or stratum; any other item's label.
Before transmission the custodian checks, by a written checklist whose SHA-256 is recorded: (1) the fields above are the only fields; (2) image files carry no revealing metadata (EXIF/filenames) in what is sent; (3) only reserve items are included; (4) the same two reference images are used for every item of a clip; (5) nothing is committed to GitHub (only the manifest hash).
