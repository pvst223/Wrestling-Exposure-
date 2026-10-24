# CMJ Evidence Freeze Closeout (V2) — Professional-Wrestling Gap Replication Attempt

Status: DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. Date: 2026-10-24. Supplements CMJ_EVIDENCE_FREEZE_CLOSEOUT_V1.md (ANA41) without overwriting it.

## 1. Scope and frozen decisions

Narrow evidence-hygiene task only. All CMJ decisions in the reviewer's list stay approved and are not re-argued: CMJ alone (Candidate #2 CLOSED/PARKED); primary = mean jump height of 3 prespecified trials, best trial = sensitivity descriptor; at most one conditional secondary = time to take-off (force-time-capable measurement only; zero is acceptable); impulse pilot-assess only; force plate preferred not required; same device and method within athlete; hands on hips; self-selected depth recorded; clock time and warm-up recorded/standardised; footwear/surface practical; inter-trial rest pilot-derived; immediate post as soon as safely/logistically feasible with exact elapsed time, no upper bound; 24 h + 48 h, 72 h conditional, 30–45 min parked; terminology "acute net neuromuscular-performance change"; PAPE reading of 24/48 h an inference; ANA40 corrections (Rampinini, Gathercole, Alba-Jiménez) approved; identifier ledger approved with documented limitations; no CMJ validation claim in professional wrestling; no injury-risk prediction claim. No pilot, equipment, data, CV, LANDING, Identity/Anatomy, Holdout #2 or Gemini work.

## 2. Reason for V2

Independent review of V1 ruled EVIDENCE FREEZE BLOCKED — GAP-SEARCH REPLICATION ONLY, because V1 used web-indexed search, not direct scholarly databases. V2 re-tests direct interface access, re-attempts the Thieme DOI, and classifies records.

## 3. Databases actually searched

**Zero direct scholarly databases were searched.** Access was re-tested today in this environment:

| Database / index | Attempt (2026-10-24) | Status |
|---|---|---|
| PubMed (E-utilities `esearch`) | `curl` through the session proxy | NOT SEARCHED — no connection (HTTP status 000; proxy tunnel refused) |
| PubMed website search | `curl`; WebFetch | NOT SEARCHED — no connection / URL not on allowlist |
| Europe PMC REST | `curl`; WebFetch (earlier) | NOT SEARCHED — no connection / not on allowlist |
| Crossref API | `curl`; WebFetch | NOT SEARCHED — no connection / not on allowlist |
| OpenAlex API | `curl`; WebFetch | NOT SEARCHED — no connection / not on allowlist |
| doi.org handle API | `curl`; WebFetch | NOT SEARCHED — no connection / not on allowlist |
| NLM MeSH API | `curl` | NOT SEARCHED — no connection |
| SPORTDiscus | no interface in this environment | NOT SEARCHED — not available |
| Scopus | no interface | NOT SEARCHED — not available |
| Web of Science | no interface | NOT SEARCHED — not available |
| Semantic Scholar API; Google Scholar | earlier attempts | NOT SEARCHED — blocked / not on allowlist |

An MCP connector registry lookup (keywords "pubmed", "biomedical literature", "scholar") found a **PubMed connector** (tools include search_articles, get_article_metadata, lookup_article_by_citation, convert_article_ids, get_full_text_article), plus Wiley Scholar Gateway, Consensus and Amass connectors. All are `installState: not_installed` and `enabledInChat: false` in this session. I cannot install or enable them from here. If the user connects the PubMed connector (it is marked authless), this replication can be run directly and the gap search closed.

## 4. Exact executed search strings

Because no database was searched, there are no database strings to report as executed. The only executed searches were web-engine supplements (general web search, not a scholarly database; these do not count as database searches):

| ID | Verbatim query | Mode | Links returned |
|---|---|---|---|
| S1 | ("professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR "pro wrestling") AND (countermovement OR CMJ OR jump OR neuromuscular OR "force plate" OR "force-time") | extended | 9 (Wikipedia/fandom/video-game pages; no scholarly record) |
| S2 | ("professional wrestlers" OR "professional wrestling" OR "pro wrestling") AND (fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance") study | extended | 9 (amateur/MMA/other items; no entertainment-wrestling performance study) |
| S3 | "professional wrestlers" physical performance OR "muscle strength" OR "jump" OR "power" cross-sectional OR cohort 2024 OR 2025 OR 2026 wrestlers WWE OR AEW OR NXT performance center | standard | 10 (amateur/national-team wrestler records and two ClinicalTrials.gov entries, titles only) |
| S4 | Lystad 2025 Thieme professional wrestling injuries Sports Medicine International Journal of Sports Medicine OR "Sportverletzung" | extended | 9 |
| S5 | thieme-connect "a-2558-7555" | standard | 10 (unrelated Thieme pages) |
| S6 | 10.1055/a-2558-7555 (earlier today) | standard | 10 (unrelated Thieme pages) |

V1's queries G1–G16, C1–C2 and P1–P4 remain as logged in V1 (also web-engine searches, not database searches). Result counts for web-engine queries are links returned (max ~10), not database hit counts.

Replication strings to run in a direct database (NOT RUN):
- PubMed: `("professional wrestling"[tiab] OR "professional wrestlers"[tiab] OR "entertainment wrestling"[tiab] OR "sports entertainment"[tiab] OR "World Wrestling Entertainment"[tiab] OR WWE[tiab] OR "pro wrestling"[tiab]) AND (countermovement[tiab] OR CMJ[tiab] OR jump*[tiab] OR neuromuscular[tiab] OR "force plate"[tiab] OR "force platform"[tiab] OR "force-time"[tiab] OR fatigue[tiab] OR recovery[tiab] OR "muscle damage"[tiab] OR "creatine kinase"[tiab] OR "physical performance"[tiab])`
- Narrower variant to limit WWE noise: replace `WWE[tiab]` with `"WWE"[tiab] AND wrestl*[tiab]`.
- Europe PMC (TITLE_ABS), Scopus (TITLE-ABS-KEY), Web of Science (TS=), SPORTDiscus (TI/AB): same concept blocks.

## 5. Result counts and screening

No database result counts exist (nothing was searched). Screening applied to the web-engine records is in §8.

## 6. Screening results (web-indexed only)

No record returned in S1–S6 or in V1's G/C/P queries measured CMJ, jump performance, neuromuscular fatigue, force-time change, or acute pre/post-match lower-extremity performance or recovery in entertainment professional wrestlers.

## 7. Thieme DOI resolution (10.1055/a-2558-7555)

RESOLVED by bibliographic record; content verified at abstract level only through a secondary page.
- Identification: a ResearchGate record states the DOI 10.1055/a-2558-7555 and PMID 40081825. A web-search result also listed the Thieme abstract URL for this DOI under "International Journal of Sports Medicine / Abstract". The Thieme page itself (abstract and PDF URLs) returned a bot-protection page and was not read.
- Title: *Epidemiology of causes and management of severe spinal injuries in elite male wrestlers*. Authors: Nana Zhao, Xiao Han, Munku Song, Junjie Liu. Year 2025 (published 11 April 2025). Journal: Int J Sports Med 46(7):525–532.
- Population: 110 elite male wrestlers, 55 Greco-Roman and 55 freestyle, surveyed on severe spinal injuries; status described only as "elite male competitive wrestlers". Greco-Roman and freestyle are Olympic-style wrestling, so this is Category C (not entertainment wrestling).
- Measures: injury survey, reinjury odds, rehabilitation and clearance; no jump, neuromuscular, force-time or pre/post-match measurement.
- Classification: C (not direct). Excluded from CMJ evidence. Caveat: abstract-level content via ResearchGate; the publisher page was not read.

## 8. Direct vs non-direct classification

| Cat. | Record | Identifier | Verified | Notes |
|---|---|---|---|---|
| A (direct, target construct) | **none identified** | — | — | — |
| B (direct, outside target) | Dei et al., Wrestler's Heart, WWE athletes, J Am Heart Assoc 2026 | DOI 10.1161/JAHA.125.046704; PMID 42294756; PMC13323589 | PMC page text | cardiac echo/ECG; no performance measure |
| B | Shean, Vedantam, Lystad, Survival and longevity in professional wrestlers, Occup Environ Med 2026 | DOI 10.1136/oemed-2025-110428; PMID 41951401 | abstract | mortality; match-exposure intensity associated with survival |
| B | Wrestling with a ghost… professional wrestlers who suffered an ACL injury, BMJ Open Sport Exerc Med 2024 | PMID 38481557; PMC10936519; DOI unresolved | abstract (DOAJ) | qualitative; 10 wrestlers |
| B | Ethnographic injury paper, independent wrestling shows, Atlantic Canada (St. Cloud State Survive & Thrive vol 8 iss 2 art 5) | repository URL; title/authors/DOI unresolved | abstract | qualitative |
| C (amateur/Olympic-style) | Zhao et al. 2025, severe spinal injuries in elite male wrestlers, Int J Sports Med | DOI 10.1055/a-2558-7555; PMID 40081825 | ResearchGate abstract | injury survey; no performance measure |
| C | Bell et al. 2023, British wrestlers injury survey | DOI 10.54080/KSMO2842 | full text | amateur/hobbyist; no performance tests |
| C | Barbas et al. 2011 Greco-Roman tournament | DOI 10.1007/s00421-010-1761-7 | abstract (repository) | jump tests not named |
| C | ClinicalTrials.gov NCT07750691 (neuromuscular predictors of vertical jump, national-team wrestlers) and NCT07792174 | registry IDs | titles only | amateur national-team wrestlers; unverified; not used |
| C | PMC12795019 (elite freestyle wrestlers, isokinetic strength vs vertical jump) | PMC ID | title only | unverified; not used |
| D (EXT, other combat/contact) | judo, BJJ, soccer, rugby, AFL, American football records | see V1 §8 | see V1 | unchanged |

## 9. Newly identified records

Newly identified this pass: Zhao et al. 2025 (Category C, §7); ClinicalTrials.gov NCT07750691 and NCT07792174 (Category C, titles only); a Nature Scientific Reports 2025 MMA fatigue paper and several amateur-wrestling records appeared as titles only and were not verified (Category C/D, not used). No new Category A or B record beyond those in V1.

## 10. Final gap wording

"No direct evidence on CMJ, jump performance, neuromuscular fatigue, force-plate/force-time change, or acute pre/post-match lower-extremity performance or recovery in entertainment professional wrestlers was identified in the web-indexed sources and search strategy examined. Direct scholarly databases (PubMed, Europe PMC, SPORTDiscus, Scopus, Web of Science) were not searched because they were not accessible in this environment. Failure to identify evidence is not proof that no such study exists."

This wording must NOT be upgraded to "databases examined" until a direct database search has been run. The terms "first-ever", "unprecedented", "no literature exists" and "never studied" are not used.

## 11. Remaining limitations

1. No direct database search (the central open issue). 
2. Web-engine results are not exhaustive and give no hit counts.
3. Thieme DOI resolved through a secondary record; the publisher page was blocked.
4. All V1 limitations carry over (unresolved identifiers for the time-of-day meta-analysis, the iPhone-app paper, the 2026 NCAA football abstract, the 2025 judo competition paper, the Kons year; lost earlier-session query strings).

## 12. Effect on the frozen CMJ methodology

None. No new record bears on any frozen CMJ decision, and no Category A record was found.

## 13. Final freeze recommendation

The key database replication still cannot be performed in this environment, so by the reviewer's own criterion the gap-search issue is not closed. The PubMed connector is available in the registry but is not installed here; connecting it (or having an investigator run the §4 strings in PubMed, Europe PMC, Scopus, Web of Science and SPORTDiscus and paste the results back) would close it. Until then, the freeze stays blocked on this single item; the CMJ science itself is unaffected.

## 14. Files created/changed

Created: v061/exposure_design/CMJ_EVIDENCE_FREEZE_CLOSEOUT_V2.md. Changed: v06/frozen/AUDIT_LEDGER.jsonl (append ANA42; no existing entry altered). No code, data, device, CV, LANDING, MP4 or frozen-branch change.

## 15. Commit / PR / ledger

Branch cmj-evidence-closeout-v2; ledger entry ANA42 (STUDY1_CMJ_EVIDENCE_FREEZE_CLOSEOUT_V2); PR number and merge commit are in the PR record.

EVIDENCE FREEZE BLOCKED
