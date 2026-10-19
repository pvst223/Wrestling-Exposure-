# M9C blinded review — instructions for the project owner (second reviewer)
You are the independent second reviewer. Please **do not look at the repository, the ledger, Claude's verdicts, or any result** until you have sent back your completed file. Do not try to work out what the system decided; judge only what you see.

**What you get:** 50 images `O000.png` … `O049.png` (private; do not share) and `OWNER_VERDICTS_TEMPLATE.csv`.
**Each image:** the left panel is the full frame; the right panel is a zoom of the same person. The **cyan box** marks the person being reviewed; thin grey boxes are other detected people. **Cyan lines and dots are the skeleton the system drew for that person.** Some images show a complete skeleton and some show only a few segments: judge exactly what is drawn, not what is missing.
**Question for every image:** do the drawn lines/points lie on the body of the person in the cyan box (not on someone else)? This says nothing about who the wrestler is.

**Verdicts (choose exactly one per image):**
- `CORRECT`: the drawn landmarks/skeleton correspond to the boxed person's anatomy without material contamination from another person.
- `PARTIAL_BUT_USABLE`: incomplete or occluded, but the drawn landmarks still correspond to the boxed person well enough to represent that person's pose (this includes skeletons with only a few segments, as long as every drawn piece is on the right body).
- `CONTAMINATED`: material drawn landmarks/segments lie on another person, or the drawing is a materially wrong body representation.
- `NOT_JUDGEABLE`: the image/occlusion, or an absence of drawn landmarks, prevents a defensible judgment.
**Optional `contact` column:** `YES` if two or more bodies visibly touch or overlap in or next to the boxed person, else `NO`. **`note`:** optional, anatomical observation only.
Judge each image on its own, in any order. Fill in `OWNER_VERDICTS_TEMPLATE.csv` (one row per owner_id, spelling exactly as above), and send it back as is. Please finish all 50 before sending; do not change answers after sending.
