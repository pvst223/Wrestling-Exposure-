# Owner decisions needed to complete the Gemini procedure freeze (reviewer conditions 1-6)

Nothing here has been decided or invoked. Do not send any Holdout #2 material to Gemini (any route) before the freeze.

1. **Model and route.** Which exact Gemini model and pinned version string (not a floating alias), and which access route (for example a paid API / Vertex AI project / enterprise workspace, versus the consumer Gemini app)? Consumer app and API/enterprise routes may handle data differently; do not assume equivalence.
2. **Settings.** On that route, the actual supported values for: temperature (lowest/0 if supported), top_p, top_k, seed (if supported), max output tokens (small), reasoning/thinking mode (fixed, same for every item), safety settings (provider default, recorded). Report which are not controllable.
3. **Disabled features.** Confirm in the console/API config that tools, web/search/grounding, memory, chat history and context carryover are off or unavailable, and that each call is a fresh stateless request with no system prompt beyond PROMPT_V1.txt.
4. **Privacy/retention review of that exact route.** Capture (save and hash) the current terms: are inputs used for training; are they reviewed by humans; retention period; whether stored prompts/logs can be deleted; region. Give your conclusion. Route with training/human review of inputs is not used unless the reviewer accepts it.
5. **No-prior-exposure statement.** Sign and date the template in section 9 of the procedure with the chosen model/route filled in; keep it private; send the SHA-256 and date.
6. **Hashes to return** (Claude computes the completed-config hash if you send me the filled JSON): filled config, privacy-review capture, owner statement. Procedure, prompt, parser and manifest-spec hashes are already fixed (see ledger GP1).

Also still open and separate: R1 (custodian), R2 (branch protection, then tooling PR), R3 (rights stance). R4 stays UNMET.
