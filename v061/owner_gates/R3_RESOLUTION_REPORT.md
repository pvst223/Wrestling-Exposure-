# R3 resolution: planning/research report (2026-10-18)

Status: planning and research only. R3 remains `UNRESOLVED / THIRD-PARTY TRANSMISSION BLOCKED` until reviewer approval. Nothing was acquired, selected, inspected, transmitted to Gemini, annotated or run. I am not a lawyer; this is not legal advice and no legal conclusion is drawn. spec_v4 and the frozen Gemini procedure v1 are unchanged.

## 1. What must be authorized (two separate questions, per source)
- **Q1 - obtain and use** the source inside the private project: copy/download, extract frames, derive crops, store privately.
- **Q2 - third-party transmission:** send the minimum frozen material (two reference images + one item crop per request) to Google Gemini via the consumer web app, only for the reserve items.

Findings that shape the standard:
- Google's Gemini Apps Privacy Hub (read 2026-10-18; page last updated October 13, 2026) says: "Only upload, generate, and edit content you have rights and permissions to," asks users to "respect others' rights," and says "Get permission before recording people in a Live chat, or using their faces or voices in Gemini." It also says not to enter "confidential information that you wouldn't want a reviewer to see." So Q2 needs a rights basis for the content AND attention to the faces of the people shown, not only copyright. (Read through a summarising fetch; the owner's hashed PDF is the authoritative capture.)
- The frozen procedure sends crops of non-target people too (`REFEREE`, `STAFF`, `SPECTATOR` are labels). Those people cannot individually consent. This is the hardest part of Q2.
- Public availability is not permission. For example, WWE's terms (read 2026-10-18) forbid copying, reproducing, uploading, archiving or downloading content without "the express written permission of WWE," forbid robots/scrapers and "any data mining, data gathering or extraction method," do not mention AI, and give cpagent@wwe.com for permissions. Terms of that kind make automated or bulk acquisition itself a Q1 problem.
- YouTube's Creative Commons help page (read 2026-10-18) says the CC BY option is for content the uploader can license (own content, content already under CC BY, or public domain), that videos with a Content ID claim cannot use it, and that "YouTube can't grant you rights to use someone else's content." So a CC label alone does not prove a chain of title.

## 2. Proposed R3 standard (per source; PASS needs every item)
**Evidence hierarchy**
- Tier 1 (sufficient basis): signed written license/permission from a verified rights holder that explicitly names both uses (Q1 and Q2).
- Tier 2 (sufficient only with verification): an open license (CC BY, public-domain dedication) plus documented chain of title for that exact work, plus written counsel confirmation for Q2 and for depicted persons.
- Tier 3 (supporting only, never alone): a written counsel opinion on an exception/fair-use theory.
- Tier 4 (zero weight): public viewability, streamability, downloadability, "research purpose," the owner's belief, or the platform's terms of access.

**PASS (per source), all of:**
1. Rights holder identified and verified; chain of title documented (for open-license material, the uploader is shown to be the rights holder).
2. Q1 authorization on record (Tier 1 or Tier 2), covering private copying, frame extraction, crop derivation, private storage.
3. Q2 authorization on record: explicit text permitting transmission of derived stills to a named third-party AI service (Gemini) for processing, or a written counsel opinion that the use is permissible under the license/terms.
4. Persons depicted: performers covered by the rights holder's talent releases/assignments or by written statement; non-target persons covered by documented event notice/ticket-terms consent or a counsel opinion, plus the existing minimisation rules.
5. Acquisition method is itself permitted (direct delivery from the rights holder, or a download the source's terms allow). No scraping and no circumvention.
6. No conflicting restriction found in the source's terms, the license, or Google's terms; any found conflict is resolved in writing.
7. Evidence stored privately, hashed, and a pseudonymous per-source record appended to the ledger (two separate fields: Q1 status, Q2 status).
8. Reviewer approves the per-source record.

**FAIL:** the rights holder refuses or the terms prohibit either use. **UNRESOLVED:** anything else, including ambiguity. A source is eligible for Holdout #2 only if PASS on both Q1 and Q2.

## 3. Candidate routes
| Route | Q1 | Q2 | Evidence found | Main gaps |
|---|---|---|---|---|
| A. Written license/permission from independent promotions | Achievable (Tier 1) | Achievable only if the agreement names third-party AI processing | None yet; needs outreach | Non-target (audience/staff) faces; acceptance unknown; need at least 2 events and 2 sources overall |
| B. Open-licensed / public-domain footage (CC BY, PD) | Tier 2 if chain of title verified | Tier 2 only with counsel confirmation | YouTube CC page above; some very old film is public domain (e.g., listings of early footage) | Chain of title per video; personality/privacy rights not cleared by a license; acquisition method (platform terms); era/domain mismatch for PD film; supply unknown |
| C. Owner-filmed with event permission | Owner holds own copyright; needs venue/promoter permission | Owner can authorize own recordings; performers' and attendees' rights still open | Owner-controlled | Travel/time; performers' and venue permissions; non-target faces; small volume |
| D. Major-promotion footage by license (e.g., WWE) | Written license required | Written license required | WWE terms above prohibit copying/data mining without express written permission; contact cpagent@wwe.com | Slow, uncertain, AI not addressed; unlikely to be granted for a student project; broadcast streams are not licensed by being viewable |
| E. Fair use / research exceptions | Not accepted as proof | Not accepted as proof | none | Reviewer ruled these insufficient alone; at most Tier 3 |

Note: the development footage already used is not in scope here; it never goes to Gemini, and its rights status stays UNRESOLVED.

## 4. Strongest route and why
**Route A**, with Route C as the owner-controlled fallback and Route B as a supplement. A single signed agreement from a rights holder who controls the footage, the talent contracts and the ticket terms can cover Q1, Q2 and most depicted persons in one document, and it is the only route whose evidence is Tier 1 by construction. B can add footage cheaply but never clears persons or Q2 by itself. D is the most valuable footage but the least likely to be obtainable. E cannot pass alone.

## 5. What each unresolved route still needs
- **A:** (i) a signed permission naming: private research use; copying and frame/crop derivation; storage; no redistribution; and transmission of derived stills to Google Gemini (consumer web app, Keep Activity off, up to 72-hour retention, possible human safety review) for annotation; (ii) a representation that the grantor owns or controls the footage and the performers' image rights, or lists exceptions; (iii) a statement on audience/staff depiction (ticket terms, filming notice) or counsel sign-off; (iv) delivery of the files directly. A draft request is in `R3_PERMISSION_REQUEST_TEMPLATE.md` (not sent).
- **B:** per video: the uploader is the rights holder (the grantor's own channel, with evidence), no Content ID claim, the exact license text, counsel confirmation for Q2 and depicted persons, and a permitted acquisition method.
- **C:** written venue/promoter filming permission, performer consent or the promoter's confirmation that performers' rights are cleared, event notice for attendees, plus Q2 wording from the promoter if they are a rights co-holder.
- **D:** a signed WWE (or equivalent) license naming both uses; otherwise FAIL/UNRESOLVED.
- All: counsel review of jurisdiction-specific points I cannot resolve (for example biometric/face-data rules where events occur, such as Illinois BIPA, and EU/UK data-protection rules). I flag these only as questions for counsel; I reach no conclusion on them.

## 6. Does a practical R3-compliant route exist without changing the frozen Gemini procedure?
**Conditionally yes, but not yet.** The frozen procedure does not need to change if Holdout #2 is built only from sources that PASS both Q1 and Q2; the procedure already blocks transmission for any other source, and the reserve is drawn from Holdout #2. The two realistic paths are a written agreement with one or more independent promotions (Route A, with Route C/B as supplements). The open risks are (a) whether a grantor will accept Q2 wording at all, and (b) the audience/staff faces, where the grantor's license cannot give individual consent and counsel input is needed. If no source can pass Q2, the only ways forward are to change the procedure (new reviewer-authorized version, for example restricting what is sent) or to drop Gemini as the second annotator; I propose neither here.
- Volume risk: Holdout #2 needs at least 4 clips, at least 8 named identities, at least 150 units, from at least 2 events and 2 sources (spec_v4 02_DATA_PLAN). The permitted pool must be large enough; not assessed.

## 7. Proposed next steps (not done; need reviewer/owner approval)
1. Reviewer approves the standard (section 2).
2. Owner decides which routes to pursue; I can customise the request template per grantor.
3. Owner sends requests; replies are hashed and recorded per source, Q1 and Q2 separately.
4. Optional: counsel review of the template and the audience-face question.

Sources read: Google Gemini Apps Privacy Hub (https://support.google.com/gemini/answer/13594961); YouTube Creative Commons help (https://support.google.com/youtube/answer/2797468); WWE Terms and Conditions (https://www.wwe.com/page/terms-and-conditions). The Google Generative AI Additional Terms page read states those terms no longer apply as of May 22, 2024 except to business partners and was not relied on.
