# Minimum owner actions to complete the Gemini freeze package (reply template)

Template only; nothing here is a statement by the owner until the owner sends it. Do all of this in a clean browser profile and upload NO study material anywhere. Nothing involving footage, frames or crops is needed for any item.

## What to do (about 15 minutes)
1. In Gemini settings: set **Keep Activity OFF**; turn off any personalization / "past chats" / saved-info features; disconnect Connected Apps you do not need. Take one screenshot per setting.
2. Open https://support.google.com/gemini/answer/13594961 and save it as a PDF. Note the date and time.
3. Compute SHA-256 of each file: macOS/Linux `shasum -a 256 FILE`; Windows PowerShell `Get-FileHash FILE -Algorithm SHA256`. Keep the files private (not in GitHub).
4. Send ONE reply containing the block below, filled in. Do not attach the screenshots/PDF to a public place.

## Reply block (fill the brackets)
```
GEMINI OWNER FIELDS
Account type: [personal consumer | Workspace/school] ; dedicated account with no other study conversations: [yes | no]
Settings verified on [DATE/TIME]: Keep Activity OFF [yes]; personalization/past chats/saved info OFF [yes | not available in my UI]; Connected Apps disconnected [yes | none connected]
Screenshot SHA-256 (one per setting): [hash1] [hash2] [hash3]
Google terms page PDF captured [DATE/TIME], SHA-256: [hash]
Retention conclusion (choose one and keep the wording):
  [ACCEPT] I accept that chats with Keep Activity off are retained for up to 72 hours for service and safety purposes, that this route is not zero-retention, and that human safety review cannot be excluded, for the reserve items from sources whose third-party transmission permission has been separately established under R3.
  [REJECT] I do not accept this retention; the consumer Gemini route will not be used.
Dated owner statement (I send this text verbatim; Claude hashes it):
  "I, CUSTODIAN-01, state on [DATE] that, apart from the single prep-only interaction I disclosed (no study material; that chat is never used for annotation), Gemini via the consumer web application has had no exposure to any Holdout #2 material, study image or crop, first-pass label, model/B0/L1 output, result, outcome, answer key or wrestler identity material before this date, that no Holdout #2 material has been entered into any Gemini interface or chat/memory feature, and that I will not do so except as the frozen procedure allows after reviewer authorization and R3 source-specific permission. This statement describes an AI annotator accurately; it is not a human independence attestation and does not satisfy R4."
```

## What Claude then does
Hashes the exact owner statement and retention conclusion text; records the file hashes; fills `GEMINI_ROUTE_CONFIG_PROPOSED.json` into a completed config (UI model designation stays RECORD_AT_RUN); computes final hashes of config, prompt, parser, procedure, reference-manifest specification, privacy record and owner statement; appends the ledger evidence; submits the freeze package to the reviewer. It is NOT frozen until the reviewer approves. Nothing is transmitted to Gemini.

## Not needed from you now
Any footage, any crop, any source list, any R3 per-source permission (those come at acquisition and gate transmission separately), and any real name.
