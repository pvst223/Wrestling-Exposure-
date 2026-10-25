# CMJ — Professional-Wrestling Database Replication Package (V1.1)

Status: DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. Prepared 2026-10-24. **No search in this package has been executed.** It is written so an investigator with database access can run it without the chat history.

## 1. Purpose

This search exists only to close the remaining professional-wrestling literature-gap evidence-hygiene gate (CMJ_EVIDENCE_FREEZE_CLOSEOUT_V2.md, ledger ANA42). It does not test, reopen or modify the frozen CMJ methodology, Candidate #2 (closed/parked), or any other frozen decision. It must not be used to design a pilot, select equipment, or support any validation or injury-risk claim.

## 2. Target construct

A record is a potential **direct** hit only if it involves **entertainment/professional wrestling** (scripted/staged performance wrestling, e.g., WWE and similar promotions) AND at least one of:

- countermovement jump / CMJ;
- jump performance;
- neuromuscular performance or fatigue;
- force plate / force platform / force-time measures;
- acute pre/post-match lower-extremity performance;
- post-match lower-extremity recovery or time course.

Distinguish entertainment professional wrestling from amateur/Olympic/collegiate/freestyle/Greco-Roman wrestling and from other combat sports. Those are NOT direct evidence (see classification in §6).

## 3. Databases

Prepare and run, in this order: PubMed; Europe PMC; SPORTDiscus; Scopus; Web of Science. Nothing below has been executed by the preparer. If a database cannot be accessed, record it as NOT SEARCHED with the reason; do not substitute a general web search.

## 4. Database-specific search strings

Conceptual blocks (approved; do not edit):

- **PROFESSIONAL-WRESTLING BLOCK:** "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling"
- **TARGET-CONSTRUCT BLOCK:** countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance"

Final query = PROFESSIONAL-WRESTLING BLOCK AND TARGET-CONSTRUCT BLOCK, restricted to title/abstract(/keywords where the database field includes them). Run **Variant A** (as approved) first. Run **Variant B** (narrower, limits WWE-acronym noise: bare `WWE` replaced by `WWE AND wrestl*`) second. Apply **no** date, language, or study-type filters, so that the full record set is counted. Use the database's default de-duplication only after recording raw counts.

Syntax status: strings were assembled programmatically from the two approved blocks, but **none was tested in a live interface** from the preparer's environment. Each database's note below says what must be confirmed. If an interface rejects or rewrites a string, record the string as actually executed (and any rewrite shown by the database) in §5; do not edit the conceptual blocks.

### 4.1 PubMed

`[tiab]` = title/abstract. The proposed PubMed query uses `jump*`/`wrestl*`; confirm their interpretation in PubMed Search Details after execution. After running, open **Search details** and record the translated query; confirm no term was dropped or auto-mapped unexpectedly. Quoted phrases containing a hyphen ("force-time") should be checked in Search details.

**PubMed — Variant A**
```
("professional wrestling"[tiab] OR "professional wrestlers"[tiab] OR "entertainment wrestling"[tiab] OR "sports entertainment"[tiab] OR "World Wrestling Entertainment"[tiab] OR WWE[tiab] OR "pro wrestling"[tiab]) AND (countermovement[tiab] OR CMJ[tiab] OR jump*[tiab] OR neuromuscular[tiab] OR "force plate"[tiab] OR "force platform"[tiab] OR "force-time"[tiab] OR fatigue[tiab] OR recovery[tiab] OR "muscle damage"[tiab] OR "creatine kinase"[tiab] OR "physical performance"[tiab])
```
**PubMed — Variant B**
```
("professional wrestling"[tiab] OR "professional wrestlers"[tiab] OR "entertainment wrestling"[tiab] OR "sports entertainment"[tiab] OR "World Wrestling Entertainment"[tiab] OR (WWE[tiab] AND wrestl*[tiab]) OR "pro wrestling"[tiab]) AND (countermovement[tiab] OR CMJ[tiab] OR jump*[tiab] OR neuromuscular[tiab] OR "force plate"[tiab] OR "force platform"[tiab] OR "force-time"[tiab] OR fatigue[tiab] OR recovery[tiab] OR "muscle damage"[tiab] OR "creatine kinase"[tiab] OR "physical performance"[tiab])
```

### 4.2 Europe PMC

`TITLE_ABS:` restricts to title+abstract. Europe PMC includes preprints and (for some records) full-text; do NOT search full text. Record the count for all sources and, separately, for MEDLINE/PubMed (`SRC:MED`) and preprints (`SRC:PPR`) if the interface lets you facet. REQUIRES INTERFACE CONFIRMATION that grouped terms and `*` truncation parse as intended.

**EuropePMC — Variant A**
```
(TITLE_ABS:"professional wrestling" OR TITLE_ABS:"professional wrestlers" OR TITLE_ABS:"entertainment wrestling" OR TITLE_ABS:"sports entertainment" OR TITLE_ABS:"World Wrestling Entertainment" OR TITLE_ABS:WWE OR TITLE_ABS:"pro wrestling") AND (TITLE_ABS:countermovement OR TITLE_ABS:CMJ OR TITLE_ABS:jump* OR TITLE_ABS:neuromuscular OR TITLE_ABS:"force plate" OR TITLE_ABS:"force platform" OR TITLE_ABS:"force-time" OR TITLE_ABS:fatigue OR TITLE_ABS:recovery OR TITLE_ABS:"muscle damage" OR TITLE_ABS:"creatine kinase" OR TITLE_ABS:"physical performance")
```
**EuropePMC — Variant B**
```
(TITLE_ABS:"professional wrestling" OR TITLE_ABS:"professional wrestlers" OR TITLE_ABS:"entertainment wrestling" OR TITLE_ABS:"sports entertainment" OR TITLE_ABS:"World Wrestling Entertainment" OR (TITLE_ABS:WWE AND TITLE_ABS:wrestl*) OR TITLE_ABS:"pro wrestling") AND (TITLE_ABS:countermovement OR TITLE_ABS:CMJ OR TITLE_ABS:jump* OR TITLE_ABS:neuromuscular OR TITLE_ABS:"force plate" OR TITLE_ABS:"force platform" OR TITLE_ABS:"force-time" OR TITLE_ABS:fatigue OR TITLE_ABS:recovery OR TITLE_ABS:"muscle damage" OR TITLE_ABS:"creatine kinase" OR TITLE_ABS:"physical performance")
```

### 4.3 Scopus

`TITLE-ABS-KEY` searches title, abstract and author/index keywords. Double-quoted phrases are loose phrases in Scopus; braces `{...}` would force exact phrases and are not used. REQUIRES INTERFACE CONFIRMATION in the Advanced search box.

**Scopus — Variant A**
```
TITLE-ABS-KEY ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) AND TITLE-ABS-KEY ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" )
```
**Scopus — Variant B**
```
TITLE-ABS-KEY ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) AND TITLE-ABS-KEY ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" )
```

### 4.4 Web of Science

`TS=` is Topic (title, abstract, author keywords, Keywords Plus). Record which Core Collection indexes your licence includes (SCI-EXPANDED, SSCI, ESCI, etc.). REQUIRES INTERFACE CONFIRMATION in Advanced Search.

**WoS — Variant A**
```
TS=( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) AND TS=( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" )
```
**WoS — Variant B**
```
TS=( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) AND TS=( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" )
```

### 4.5 SPORTDiscus (EBSCOhost)

`TI` = title, `AB` = abstract (EBSCO field codes). Field-code boxes and operators differ between EBSCO interfaces; this string is a best-effort translation and REQUIRES INTERFACE CONFIRMATION (use the field-select dropdowns if typed codes are rejected). Keywords/subject fields (`KW`/`SU`) are deliberately not added to keep the approved title/abstract scope.

**SPORTDiscus — Variant A**
```
( TI ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) OR AB ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR WWE OR "pro wrestling" ) ) AND ( TI ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) OR AB ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) )
```
**SPORTDiscus — Variant B**
```
( TI ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) OR AB ( "professional wrestling" OR "professional wrestlers" OR "entertainment wrestling" OR "sports entertainment" OR "World Wrestling Entertainment" OR (WWE AND wrestl*) OR "pro wrestling" ) ) AND ( TI ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) OR AB ( countermovement OR CMJ OR jump* OR neuromuscular OR "force plate" OR "force platform" OR "force-time" OR fatigue OR recovery OR "muscle damage" OR "creatine kinase" OR "physical performance" ) )
```

## 5. Execution log (investigator to complete)

One row per executed query (Variant A and Variant B separately for each database).

| Database / interface | Date searched | Variant | Exact final query as executed | Filters / fields / indexes | Result count (raw) | Records screened | Potentially relevant records (IDs from §6) | Notes (rewrites, warnings, access limits) |
|---|---|---|---|---|---|---|---|---|
| PubMed | | A | | | | | | |
| PubMed | | B | | | | | | |
| Europe PMC | | A | | | | | | |
| Europe PMC | | B | | | | | | |
| SPORTDiscus | | A | | | | | | |
| SPORTDiscus | | B | | | | | | |
| Scopus | | A | | | | | | |
| Scopus | | B | | | | | | |
| Web of Science | | A | | | | | | |
| Web of Science | | B | | | | | | |

Any database not searched: write NOT SEARCHED and the reason in Notes.

Screening procedure: de-duplicate across databases after recording raw counts; screen every title/abstract (not only the first page); for each potentially relevant record, obtain the abstract (full text when needed to decide A vs B) and fill §6. State the screening reviewer(s) and whether a second person screened.

## 6. Record-screening template

Classification: **A** = direct entertainment professional wrestling + target construct. **B** = direct entertainment professional wrestling but outside the target construct. **C** = amateur/Olympic/collegiate/freestyle/Greco-Roman wrestling. **D** = other combat/contact sport or other EXT population.

| ID | Title | Authors | Year | Journal / source | DOI | PMID / other stable ID | Abstract / full text available | Population | Entertainment professional wrestling? (YES/NO/UNCLEAR) | Target construct present? (YES/NO/UNCLEAR) | Class (A/B/C/D) | Inclusion / exclusion reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | | | | | | | | | | | | |

If population status (professional/entertainment vs amateur) is not stated, record UNCLEAR and the class that would apply under each reading; do not guess.

## 7. Known records (duplicate check)

These were identified earlier. Recognise them as duplicates; do not count them as evidence for the CMJ construct.

| Record | Identifier | Class |
|---|---|---|
| Dei et al. 2026, Wrestler's Heart: Cardiac Remodeling in World Wrestling Entertainment Athletes, J Am Heart Assoc 15(12):e046704 | DOI 10.1161/JAHA.125.046704; PMID 42294756; PMC13323589 | B |
| Shean, Vedantam & Lystad 2026, Survival and longevity in professional wrestlers, Occup Environ Med 83(2):107-112 | DOI 10.1136/oemed-2025-110428; PMID 41951401 | B |
| "Wrestling with a ghost: facing an opponent I can neither see nor clinch – the experience of professional wrestlers who have suffered an ACL injury", BMJ Open Sport Exerc Med 2024 (qualitative) | PMID 38481557; PMC10936519; DOI not recovered | B |
| Ethnographic paper on injuries in independent wrestling shows, Atlantic Canada (St. Cloud State "Survive & Thrive" vol 8 iss 2 art 5) | repository URL repository.stcloudstate.edu/survive_thrive/vol8/iss2/5; title/authors/DOI not recovered | B |
| Zhao N et al. 2025, Epidemiology of causes and management of severe spinal injuries in elite male wrestlers, Int J Sports Med 46(7):525-532 (Greco-Roman and freestyle) | DOI 10.1055/a-2558-7555; PMID 40081825 | C |

## 8. Decision rule

- **If ANY Category A record is identified:** do NOT alter the CMJ methodology; do NOT silently assimilate it; return the record for independent review; the evidence freeze stays blocked until its implications are assessed.
- **If NO Category A record is identified after the database searches** (and every database in §3 is either searched or explicitly listed as NOT SEARCHED with reason), the gap wording may become:

> "No direct evidence on CMJ, jump performance, neuromuscular fatigue, force-plate/force-time change, or acute pre/post-match lower-extremity performance or recovery in entertainment professional wrestlers was identified in the databases and search strategy examined. Failure to identify evidence is not proof that no such study exists."

If any of the five databases was NOT SEARCHED, the wording must name the unsearched databases. Do not use "first-ever," "unprecedented," "no literature exists," or "never studied."

## 9. Return format for the completed search

Return one document with these headings, in this order:

1. Databases searched (name, interface/vendor, index coverage or licence notes) and databases NOT SEARCHED with reasons.
2. Dates searched (each database).
3. Exact queries as executed (verbatim, including any database rewrite).
4. Result counts (raw per query; then de-duplicated total).
5. Screened records (the §6 table, one row per potentially relevant record; also list the count excluded at title/abstract).
6. Category A records (state "none" or list with full citation, DOI/PMID, and abstract).
7. Unresolved records (could not obtain abstract/full text, or population status unclear).
8. Final notes (deviations from this package, screeners, anything unexpected).

## 10. Current project status

The CMJ methodology is substantively frozen. The only open evidence-freeze item is direct database replication of the professional-wrestling gap search. No pilot-design work should begin as part of this package.

## 11. Files / version control

V1.1 supersedes V1 (ledger ANA43, PR #69), which is left unchanged. V1.1 differs from V1 only in (a) the PubMed truncation sentence in §4.1, replaced at the independent reviewer's direction so the package does not assert PubMed behaviour that has not been verified in the live interface, and (b) this version label and §11. Created: v061/exposure_design/CMJ_PRO_WRESTLING_DATABASE_REPLICATION_PACKAGE_V1_1.md. Changed: v06/frozen/AUDIT_LEDGER.jsonl (append ANA44; no existing entry altered). CMJ_EVIDENCE_FREEZE_CLOSEOUT_V1.md and V2 are unchanged. Branch cmj-replication-package-v1-1; ledger entry ANA44 (STUDY1_CMJ_DATABASE_REPLICATION_PACKAGE_V1_1); the PR number and merge commit are in the PR record.
