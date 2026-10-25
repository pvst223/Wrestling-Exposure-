# CMJ Professional-Wrestling Database Replication — Completed Report (V1)

Status: DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. Prepared 2026-10-25 from the investigator's manual execution summary (received 2026-10-25 14:31 ET), audited against the frozen package `CMJ_PRO_WRESTLING_DATABASE_REPLICATION_PACKAGE_V1_1.md` (sha256 0ac952416e4046633e346a9e346c7434998c465ec22fc78c63471cbfd5a680f6, verified identical to the file the investigator was given) and the Post-CMJ Freeze Checkpoint V1. This audit did not re-run any search and relied on the investigator's summary. No frozen CMJ, Candidate #2, exposure, CV, LANDING, Identity/Anatomy, Holdout #2 or Gemini decision was touched.

## A. Audit ruling

**EVIDENCE FREEZE CLOSED — with documented limitations (below).** Reason: the frozen package's decision rule (§8) is met. Three of five databases were genuinely searched; the other two are recorded NOT SEARCHED with reasons; no Category A record was identified; no record described requires Category A status. The permitted gap wording may be adopted, but only in the form that names the two unsearched databases (§10 below). The closure rests on the investigator's screening summary and carries a tripwire: if the two items in §C.1–C.2 turn out to show a quantitative lower-extremity neuromuscular or performance measure in entertainment professional wrestlers, the freeze reverts to blocked and the record goes to independent review.

## 1. Databases searched; interfaces/index coverage; NOT SEARCHED reasons

| Database | Status | Interface / coverage | Notes |
|---|---|---|---|
| PubMed | SEARCHED | NCBI PubMed web interface; Search Details confirmed Title/Abstract execution | Warning recorded: "Quoted phrase not found in phrase index: entertainment wrestling." |
| Europe PMC | **NOT SEARCHED** | — | Repeated attempts: the search interface would not load/render. No web-search substitute used. |
| SPORTDiscus with Full Text | SEARCHED | EBSCOhost via Nova Southeastern University | Field codes and fields actually used were not supplied (see §8 gaps). |
| Scopus | **NOT SEARCHED** | — | Institutional (NSU) access provided Scopus Preview only (source/author functions), not document search, so the frozen TITLE-ABS-KEY query could not be executed. No web-search substitute used. |
| Web of Science Core Collection | SEARCHED | Clarivate; Editions: All; Topic search; no date filters | Which indexes the institutional licence includes was not supplied (see §8 gaps). |

## 2. Dates

Search dates were not supplied. The searches were done after the project was parked at the execution gate (2026-10-25 12:13 ET) and before the results were received (2026-10-25 14:31 ET); this window is inferred from message timestamps and is not a recorded search date. Documentation gap (§8).

## 3. Exact queries

The investigator states that the frozen package was followed. As-executed strings were not supplied, so none is invented here. The queries to be taken as executed are the frozen package strings, reproduced from the package unchanged:

**PubMed — Variant A (package §4.1)**
```
("professional wrestling"[tiab] OR "professional wrestlers"[tiab] OR "entertainment wrestling"[tiab] OR "sports entertainment"[tiab] OR "World Wrestling Entertainment"[tiab] OR WWE[tiab] OR "pro wrestling"[tiab]) AND (countermovement[tiab] OR CMJ[tiab] OR jump*[tiab] OR neuromuscular[tiab] OR "force plate"[tiab] OR "force platform"[tiab] OR "force-time"[tiab] OR fatigue[tiab] OR recovery[tiab] OR "muscle damage"[tiab] OR "creatine kinase"[tiab] OR "physical performance"[tiab])
```
**PubMed — Variant B (package §4.1)**
```
("professional wrestling"[tiab] OR "professional wrestlers"[tiab] OR "entertainment wrestling"[tiab] OR "sports entertainment"[tiab] OR "World Wrestling Entertainment"[tiab] OR (WWE[tiab] AND wrestl*[tiab]) OR "pro wrestling"[tiab]) AND (countermovement[tiab] OR CMJ[tiab] OR jump*[tiab] OR neuromuscular[tiab] OR "force plate"[tiab] OR "force platform"[tiab] OR "force-time"[tiab] OR fatigue[tiab] OR recovery[tiab] OR "muscle damage"[tiab] OR "creatine kinase"[tiab] OR "physical performance"[tiab])
```
**SPORTDiscus — Variant A (package §4.5)**
```
( TI ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) OR AB ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) ) AND ( TI ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) OR AB ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) )
```
**SPORTDiscus — Variant B (package §4.5)**
```
( TI ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) OR AB ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) ) AND ( TI ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) OR AB ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) )
```
**Web of Science — Variant A (package §4.4)**
```
TS=( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) AND TS=( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" )
```
**Web of Science — Variant B (package §4.4)**
```
TS=( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) AND TS=( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" )
```
Europe PMC (package §4.2) and Scopus (package §4.3) strings: NOT EXECUTED. Documented implementation: PubMed Search Details confirmed Title/Abstract execution; Web of Science used the Topic field (TS=); the SPORTDiscus field codes actually entered, and any rewrite shown by EBSCO or Web of Science, were not supplied.

## 4. Raw counts, then de-duplicated total

| Database | Variant A raw | Variant B raw | Removed by B |
|---|---|---|---|
| PubMed | 13 | 2 | 11 (not itemized) |
| Europe PMC | NOT SEARCHED | NOT SEARCHED | — |
| SPORTDiscus | 9 | 7 | 2 (identified: Walk With Ease; a non-target WWE fitness/supplement item; both bare-WWE noise) |
| Scopus | NOT SEARCHED | NOT SEARCHED | — |
| Web of Science | 27 | 10 | 17 (not itemized) |
| **Sum of raw counts** | **49** | **19** | |

De-duplicated cross-database total: **not supplied and not computable from the counts given**; no de-duplication result is invented. Variant B only narrows the bare-WWE term, so each Variant B set is a subset of its Variant A set; screening of the Variant A sets therefore covers Variant B.

## 5. Screened records and title/abstract exclusion count

Exclusion count at title/abstract: **not supplied** (documentation gap). Records the investigator described, classified by this audit (A/B/C/D as defined in package §6). Where the supplied description is insufficient, the field is UNCLEAR and no class is guessed beyond the stated provisional.

| ID | Record (as described) | Source | Entertainment pro wrestling? | Target construct? | Class | Reason / status |
|---|---|---|---|---|---|---|
| R1 | "Piussi et al." professional-wrestling ACL study | PubMed; WoS | YES (professional wrestlers) | NO (qualitative injury experience, as described) | **B** | Appears to be the known record "Wrestling with a ghost…" (BMJ Open Sport Exerc Med 2024, PMID 38481557); first-author identity is not verified here. Duplicate of package §7 pending confirmation (§C.3). |
| R2 | Supplementation protocol in "semi-professional competitive wrestling" | PubMed | NO per description (competitive wrestling), UNCLEAR whether "semi-professional" means sports entertainment | UNCLEAR (supplementation protocol; outcome measures not described) | **C (provisional)** | Needs abstract check (§C.2). |
| R3 | Force-platform hopping study in wrestlers (leg stiffness, passive muscle mechanical properties) | SPORTDiscus | NO (abstract describes conventional sport wrestling) | YES (force platform, lower-extremity) | **C** | Not entertainment professional wrestling; not Category A. |
| R4 | Walk With Ease | SPORTDiscus (Variant A only) | NO (WWE acronym noise) | — | excluded | Not wrestling. |
| R5 | Non-target WWE fitness/supplement item | SPORTDiscus (Variant A only) | NO (acronym noise) | — | excluded | Not wrestling. |
| R6 | Women's pro-wrestling physical-performance/history chapter | WoS | YES (as described) | **UNCLEAR** ("physical performance" in a history chapter; measurement content not described) | **B (provisional)** | Title, authors and identifier not supplied; cannot be classified defensibly from the description (§C.1). |
| R7 | Competitive/semi-professional wrestling studies (not itemized) | WoS | NO per description | NOT STATED | **C (provisional)** | Not itemized; the investigator reports none tested the target construct in entertainment professional wrestlers. |
| R8 | Unrelated search-term noise | WoS | NO | — | excluded | Not itemized. |

## 6. Category A records

None identified by the investigator; none required by this audit's classification of the records described. Two items (R6, R2) are held as provisional B/C on incomplete description and are listed as unresolved in §7. Known records from package §7 (Dei 2026; Shean 2026; BMJ OSEM ACL; Atlantic Canada ethnography; Zhao 2025) were not reported as re-found except R1, which matches the BMJ OSEM record by description. They remain B/B/B/B/C and are not evidence for the CMJ construct.

## 7. Unresolved records

1. R6: women's pro-wrestling physical-performance/history chapter (WoS): entertainment wrestling YES; target-construct content UNCLEAR; identifiers not supplied.
2. R2: semi-professional competitive-wrestling supplementation protocol (PubMed): population status and outcome measures UNCLEAR; identifiers not supplied.
3. R1: identity as the known BMJ OSEM record not verified (first author "Piussi" supplied by the investigator).
4. The 11 PubMed and 17 WoS records removed by Variant B are not itemized (they remain within Variant A screening).

## 8. Final notes, deviations, screeners, unexpected findings

- **Deviations from the package:** Europe PMC and Scopus NOT SEARCHED (reasons in §1). The package allows this (§3, §8) but requires the gap wording to name the unsearched databases.
- **Documentation gaps (not invented):** exact search dates; as-executed strings for SPORTDiscus and Web of Science and any database rewrites; SPORTDiscus fields used; Web of Science index coverage under the licence; de-duplicated total; title/abstract exclusion count; screener identity and whether a second person screened; identifiers for R2, R6, R7.
- **PubMed warning:** the unmatched phrase "entertainment wrestling" is expected to contribute no matches; how PubMed treated it inside the OR group was not documented beyond the warning. The other phrases in the block ran.
- **Unexpected findings:** none that changes any frozen decision. Bare-WWE noise was confirmed in SPORTDiscus, which supports the purpose of Variant B.
- **Coverage limits:** preprints and full-text-derived records (Europe PMC) and Scopus-only indexed journals were not searched. The earlier web-indexed searches (closeouts V1/V2) are not database searches and do not fill these gaps.

## 9. Decision rule applied

Package §8: no Category A record after the databases were searched or listed NOT SEARCHED with reasons, so the gap wording may become the bounded form. Because two databases were NOT SEARCHED, the wording must name them.

## 10. Adopted gap wording

"No direct evidence on CMJ, jump performance, neuromuscular fatigue, force-plate/force-time change, or acute pre/post-match lower-extremity performance or recovery in entertainment professional wrestlers was identified in the databases and search strategy examined (PubMed, SPORTDiscus with Full Text and Web of Science Core Collection; Europe PMC and Scopus were NOT SEARCHED). Failure to identify evidence is not proof that no such study exists."

The terms "first-ever," "unprecedented," "no literature exists," and "never studied" are not used and are not supported.

## C. Items for the project owner's review

1. **R6 (WoS chapter):** please supply title, authors and abstract. If the abstract reports a quantitative lower-extremity neuromuscular, jump or performance measurement in entertainment professional wrestlers, it becomes Category A and the freeze reverts to blocked.
2. **R2 (PubMed supplementation protocol):** please confirm the population is sport (not entertainment) wrestling and note any outcome measures. Same tripwire.
3. **R1:** please confirm it is the known BMJ OSEM 2024 qualitative record (PMID 38481557).
4. If available, add the search dates, SPORTDiscus fields, WoS index coverage, de-duplicated total, exclusion count and screener(s). These would tighten the record; they do not change the ruling unless they reveal a Category A record.

## D. Updated checkpoint / ledger

Checkpoint V2 (`PROSPECTIVE_STUDY1_POST_CMJ_FREEZE_CHECKPOINT_V2.md`) supersedes V1 without altering it; ledger entry ANA47 records this report and checkpoint V2. All frozen hashes are preserved.

## E. Next scientific phase

The next scientific phase is reliability/methodology pilot design. It has not been designed or started here.
