# CMJ Evidence Freeze Closeout (V1)

Status: DESIGN/RESEARCH ONLY. ANNOTATION_PROVISIONAL. Search date for everything below: 2026-10-24. Supplements, does not overwrite, CMJ_EVIDENCE_VERIFICATION_PRE_PILOT_FREEZE_V1.md (ledger ANA40).

## 1. Scope and non-actions

Done: (a) a search for entertainment/professional-wrestling literature on CMJ / jump / neuromuscular / force-time / acute pre-post lower-extremity performance and recovery; (b) a self-contained search and identifier ledger for the CMJ evidence package.

Not done, by instruction: no pilot design, no equipment selection, no data, no CV/LANDING/Identity-Anatomy/Holdout #2/Gemini work, Candidate #2 stays CLOSED/PARKED, no second neuromuscular test, impulse NOT promoted, no wrestling validation claim, no injury-risk claim.

## 2. Independent-review rulings being implemented

Approved decisions below are carried unchanged and not re-argued: primary = mean jump height of 3 prespecified trials (best trial = sensitivity descriptor only); at most ONE conditional secondary = time to take-off, only with force-time-capable measurement (zero is acceptable with flight-time-only); impulse = pilot-assess only; force plate preferred not required; same device and calculation method within athlete; hands on hips; self-selected depth recorded when possible; clock time and warm-up recorded/standardised; footwear/surface standardised on practical grounds; inter-trial rest and immediate-post upper bound unfrozen/pilot-derived; immediate post = as soon as safely/logistically feasible with exact elapsed time; 24 h + 48 h, 72 h conditional, 30–45 min parked; terminology = acute net neuromuscular-performance change; PAPE reading of 24/48 h deficits is an inference; typical error, reference-session number, inter-trial rest, post window, depth drift, time-to-take-off usefulness, possible impulse promotion and need for 72 h are pilot-derived.

## 3. Search methods (and the limit on "database-grade")

**The strongest search available to me is NOT a direct database query.** In this environment, direct access failed:

| Source | Attempt | Result |
|---|---|---|
| PubMed E-utilities (eutils.ncbi.nlm.nih.gov) | curl from shell | HTTP 403 (proxy tunnel refused) |
| Europe PMC REST | curl; WebFetch (earlier pass) | 403; URL_NOT_ON_ALLOWLIST |
| Crossref API | curl | 403 |
| OpenAlex API | curl; WebFetch | 403; URL_NOT_ON_ALLOWLIST |
| Semantic Scholar API | curl | 403 |
| PubMed web search (pubmed.ncbi.nlm.nih.gov/?term=…) | WebFetch | URL_NOT_ON_ALLOWLIST |
| Google Scholar | WebFetch | URL_NOT_ON_ALLOWLIST |
| PMC article pages | WebFetch | often reCAPTCHA interstitial (PMC9778897, PMC10936519, PMC10463540, PMC6316300); some URLs not on allowlist (PMC11782285, PMC8950744, PMC9865236 on pmc.ncbi.nlm.nih.gov) |
| PubMed article pages | WebFetch | some fetched (PMID 41951401, 24912201, 29098658 via other pages); some reCAPTCHA/client_error (29098658 direct, 38481557) |
| Thieme-Connect | WebFetch | bot-protection interstitial |

Method actually used: WebSearch (a general web search engine; "standard" and "extended" modes), including queries restricted to biomedical-database domains (pubmed.ncbi.nlm.nih.gov, ncbi.nlm.nih.gov, pmc.ncbi.nlm.nih.gov, europepmc.org) and to publisher/aggregator domains (ScienceDirect, Springer, Taylor & Francis, LWW, MDPI, Frontiers, Sage, Wiley, ResearchGate, Semantic Scholar), followed by WebFetch of result pages. A search engine returns at most ~10 links per query and no total hit count, so the "results" figure below is links returned, not a database hit count. This is a web-indexed search, not a database search; it cannot establish exhaustive coverage. Embase, Scopus, Web of Science, SPORTDiscus were not available.

## 4. Exact search log

Tool: WebSearch. "Domains" = the allowed_domains filter used (none = unrestricted). "Links" = results returned (max 10; no total count available).

**A. Entertainment / professional wrestling gap queries**

| ID | Verbatim query | Mode | Domains | Links |
|---|---|---|---|---|
| G1 | "professional wrestlers" countermovement jump | standard | pubmed, ncbi, europepmc | 10 |
| G2 | "professional wrestling" neuromuscular fatigue | standard | pubmed, ncbi, europepmc | 3 |
| G3 | "professional wrestling" physiological demands match | standard | pubmed, ncbi, europepmc | 4 |
| G4 | "professional wrestlers" force plate OR jump OR recovery OR fatigue | standard | semanticscholar, researchgate, sciencedirect, springer, link.springer, tandfonline, journals.lww, mdpi, frontiersin, sagepub, wiley | 3 |
| G5 | "entertainment wrestling" OR "sports entertainment" wrestlers injury performance study | standard | none | 9 |
| G6 | "professional wrestlers" heart rate OR "creatine kinase" OR "muscle damage" OR "match load" scripted match | extended | none | 9 |
| G7 | WWE OR AEW OR "independent wrestling" wrestlers countermovement jump OR "vertical jump" OR "force plate" OR "post-match" | extended | none | 9 |
| G8 | professional wrestling athletes exercise science physiological profile body composition strength study journal | standard | none | 10 |
| G9 | "professional wrestlers" injuries epidemiology OR survey OR cohort journal | standard | none | 10 |
| G10 | "professional wrestling" "strength and conditioning" OR "performance testing" OR "physical performance" wrestlers study | standard | none | 10 |
| G11 | "World Wrestling Entertainment" OR WWE athletes study journal medicine exercise | standard | pubmed, pmc, ncbi, europepmc, sciencedirect, sagepub, bmj, springer, link.springer | 7 |
| G12 | Lystad professional wrestling injury epidemiology | standard | none | 9 |
| G13 | professional wrestling match physiological load heart rate accelerometer study "professional wrestling" | standard | pubmed, pmc, researchgate, sciencedirect, tandfonline, lww, mdpi, semanticscholar, sportrxiv, osf, core | 2 |
| G14 | "pro wrestling" OR "professional wrestling" "countermovement" OR "neuromuscular" OR "force platform" preprint OR thesis OR dissertation | extended | none | 9 |
| G15 | "professional wrestling" injuries OR concussion OR "musculoskeletal" wrestlers retrospective OR prospective study PubMed | standard | pubmed, pmc, europepmc, thieme-connect, bmjopensem, sagepub | 10 |
| G16 | "scripted" OR "staged" combat sport wrestlers neuromuscular performance jump "professional wrestlers" training load monitoring | extended | none | 10 |

**B. Amateur wrestling and other combat sports**

| ID | Verbatim query | Mode | Domains | Links |
|---|---|---|---|---|
| C1 | wrestlers "countermovement jump" before and after match OR competition recovery 24 h freestyle OR Greco-Roman OR collegiate | standard | none | 10 |
| C2 | mixed martial arts OR boxing OR taekwondo OR karate countermovement jump after fight OR bout neuromuscular fatigue pre post | standard | none | 10 |

**C. Earlier pass (2026-10-24, final protocol-gap pass; verbatim)**

| ID | Verbatim query | Mode |
|---|---|---|
| P1 | countermovement jump self-selected versus controlled countermovement depth jump height reliability | standard |
| P2 | time of day diurnal variation countermovement jump performance systematic review meta-analysis | standard |
| P3 | rest interval between countermovement jump trials reliability jump height | standard |
| P4 | warm-up effect on countermovement jump performance dynamic stretching meta-analysis | standard |

**D. Earlier-session queries (CMJ reliability, force-time variables, device agreement, post-match time course, PAP/PAPE, judo/BJJ/wrestling CMJ, professional-wrestling terms; ~16 queries).** Their verbatim strings were recorded only in the session transcript and were NOT preserved in the repository. They cannot be reconstructed verbatim and are therefore listed here as **UNRESOLVED (strings lost)**. Every source those queries surfaced and that is used in the package was re-identified below by title, so no decision depends on the lost strings.

**E. Identifier-recovery queries (title + author + journal + year, run today)** for: Silva 2018; Ruf 2024; Balsalobre-Fernández 2015; Glatthorn 2011; Claudino 2017; Cormack 2008a; Cormack 2008b; Gathercole 2015; Blazevich & Babault 2019; Seitz & Haff 2016; Tillin & Bishop 2009; Rampinini 2011; Alba-Jiménez 2022; Anicic 2023; Hopkins 2000; Esteban-García 2024; Johnston 2013; DOI string 10.1055/a-2558-7555; and "Wrestling with a ghost…" (exact strings not individually reproduced here; each was the work's title plus first author, year and journal as named).

**F. Recommended replication strings (NOT RUN; for an investigator with database access)**
- PubMed: `("professional wrestling"[tiab] OR "professional wrestlers"[tiab] OR "entertainment wrestling"[tiab] OR "sports entertainment"[tiab] OR "World Wrestling Entertainment"[tiab] OR "WWE"[tiab]) AND (jump*[tiab] OR "countermovement"[tiab] OR neuromuscular[tiab] OR "force plate"[tiab] OR "force platform"[tiab] OR fatigue[tiab] OR recovery[tiab] OR "muscle damage"[tiab] OR "creatine kinase"[tiab])`
- Same concept block in Europe PMC (TITLE_ABS), Scopus (TITLE-ABS-KEY), Web of Science (TS=), SPORTDiscus (AB/TI). Also search for "pro wrestling", "wrestlers" AND "kayfabe"/"scripted", and sportRxiv/medRxiv/OSF preprints.

## 5. Search results and screening

**Direct entertainment/professional-wrestling records identified (all outside the target construct):**

| Record | Identifier | Verified | Content | Screening |
|---|---|---|---|---|
| Dei LL et al., Wrestler's Heart: Cardiac Remodeling in World Wrestling Entertainment Athletes. J Am Heart Assoc 2026;15(12):e046704 | DOI 10.1161/JAHA.125.046704; PMID 42294756; PMCID PMC13323589 | PMC page text read | 68 WWE European training-division athletes; resting ECG and echocardiography | Direct pro-wrestling; NOT neuromuscular; no jump, strength, or pre/post match measure. Exclude from CMJ evidence. |
| Shean J, Vedantam S, Lystad RP. Survival and longevity in professional wrestlers: a retrospective cohort study. Occup Environ Med 2026;83(2):107-112 | DOI 10.1136/oemed-2025-110428; PMID 41951401 | Abstract | 1,012 WWE-lineage wrestlers; survival; match-exposure intensity associated with survival (HR 1.71) | Direct pro-wrestling; mortality outcome; NOT neuromuscular. Exclude from CMJ evidence. Note: relevant to the exposure construct only as background. |
| Wrestling with a ghost: facing an opponent I can neither see nor clinch – the experience of professional wrestlers who have suffered an ACL injury. BMJ Open Sport Exerc Med 2024 | PMID 38481557; PMCID PMC10936519; DOI unresolved | Abstract only (via DOAJ record); PubMed/PMC pages blocked | 10 professional wrestlers, qualitative interviews | Direct pro-wrestling; lower-limb injury experience; qualitative; no performance measures. Exclude from CMJ evidence. |
| Ethnographic paper on injuries in independent wrestling shows in Atlantic Canada, St. Cloud State "Survive & Thrive" vol 8 iss 2 art 5 | repository URL only (repository.stcloudstate.edu/survive_thrive/vol8/iss2/5); title, authors, DOI unresolved | Abstract only | 4 observed cases, ethnographic | Direct pro-wrestling; qualitative; no performance measures. Exclude. |
| Macquarie University news item on professional wrestler survival | web page, no DOI | News page | Secondary reporting of the survival cohort | Not a study record; not cited. |

**Amateur wrestling (NOT direct evidence):** Bell et al. 2023, injury survey of British wrestlers, DOI 10.54080/KSMO2842 (abstract and full-text content read; amateur/hobbyist athletes, self-report injuries, no performance tests). Barbas et al. 2011 Greco-Roman tournament (DOI 10.1007/s00421-010-1761-7; repository abstract; jump tests not named). PMC12795019 (elite freestyle wrestlers, isokinetic strength vs vertical jump, cross-sectional) and PMC10464753 (CMJ force-time consistency in combat fighters): **seen as search-result titles only; not verified; not used.**

**Other combat sports (EXT, not direct):** Orssatto 2019, da Silva 2014, Kons (year unresolved), Serrano-Huete 2023 (as in ANA40), plus two records found in this pass: Chang et al. 2022 (judo training session; CMJ on force plate before, immediately after, 12 h and 24 h; neuromuscular fatigue detected only at 24 h, not immediately after; abstract) and Assessing post-competition recovery in judo, Res Sports Med 2025;33(4):448-457, DOI 10.1080/15438627.2025.2471384 (13 junior judo athletes; CK rose at 24 h; CMJ unchanged across 24 h pre, 24 h post, 48 h post; abstract). Mixed-martial-arts / Muay Thai / jiu-jitsu CMJ records appeared (titles only) and were not verified.

**Result of screening:** among all records returned, none measured CMJ, jump performance, neuromuscular fatigue, force-plate/force-time change, or acute pre/post-match lower-extremity performance or recovery in entertainment professional wrestlers.

**Unresolved record that could not be screened:** a Thieme-Connect PDF (DOI 10.1055/a-2558-7555) surfaced under G12 (Lystad, professional wrestling injury epidemiology); the page was blocked (bot-protection), a DOI search returned nothing, and its title/content is UNKNOWN. It is recorded as an unscreened potential record, not as evidence of absence.

## 6. Direct vs EXT evidence separation

- **Direct (entertainment professional wrestling):** none for the target construct. Four direct records exist on other outcomes (cardiac structure; mortality; qualitative ACL experience; ethnographic injury). None supports or tests any frozen CMJ assumption; none contradicts it.
- **Amateur wrestling:** no verified CMJ result.
- **Other combat sports (EXT):** simulated judo bouts and training (CMJ falls in some, not in others), BJJ simulated fights (no impairment 20 min after), junior judo competition (CMJ unchanged at 24/48 h while CK rose). Results are mixed; all simulated or non-scripted sports.
- **Team/contact (EXT):** soccer, rugby, AFL, American football.
- **Generic methodology:** device agreement, arm swing, depth, time of day, warm-up, PAPE.

Novelty/impact statement: no entertainment-wrestling record found affects any frozen assumption or the novelty statement as worded. The novelty statement must remain "not identified in the sources searched", not "unprecedented".

## 7. Final professional-wrestling gap wording

"No direct evidence on CMJ, jump performance, neuromuscular fatigue, force-plate or force-time change, or acute pre/post-match lower-extremity performance or recovery in entertainment professional wrestlers was identified in the web-indexed sources and search strategy examined (general web search, including queries restricted to PubMed, PMC and Europe PMC domains, 2026-10-24). Direct professional-wrestling studies that were identified addressed cardiac structure, mortality, and qualitative injury experience. Direct database interfaces (PubMed, Europe PMC, Scopus, Web of Science) were not queryable in this environment, one potentially relevant record could not be screened, and absence of evidence here is not proof that no such study exists."

This wording is the strongest supportable one. A "database-grade" search as specified was NOT achieved.

## 8. Reproducibility / identifier ledger

Legend: Verification = full text / abstract / metadata (title and bibliographic record only). Class = EXT (other sport/population), GEN (generic methodology), DIR (direct pro wrestling, not used for CMJ decisions).

| # | Source | Identifier | Verification | Class | Decision supported |
|---|---|---|---|---|---|
| 1 | Silva JR et al. Acute and residual soccer match-related fatigue: SR/MA. Sports Med 2018;48(3):539-583 | DOI 10.1007/s40279-017-0798-8; PMID 29098658 | full text (earlier pass); bibliographic record today | EXT | 24/48 h schedule; 72 h conditional; CMJ time course |
| 2 | Akyildiz Z et al. Monitoring post-match neuromuscular fatigue of young Turkish football players. Sci Rep 2022;12:13835 | DOI 10.1038/s41598-022-17831-7 | full text | EXT | 24/48 h |
| 3 | Marqués-Jiménez D et al. Recovery kinetics of CMJ after soccer matches. Eur J Hum Mov 2025;54:65-75 | DOI 10.21134/eurjhm.2025.54.9 | abstract | EXT | post/24/48 h; propulsive phase |
| 4 | Grainger A. Recovery and restoration of performance in elite rugby union. PhD thesis, Univ. Salford, 2017 | repository record; no DOI | abstract | EXT | long recovery; single-CMJ fallback |
| 5 | Orssatto LBR et al. Photobiomodulation does not attenuate fatigue… judo. Front Physiol 2019;10:811 | DOI 10.3389/fphys.2019.00811 | full text | EXT | impulse persistence at 24/48 h (pilot-assess) |
| 6 | da Silva BVC et al. Neuromuscular responses to simulated BJJ fights. J Hum Kinet 2014;44:249-257 | DOI 10.2478/hukin-2014-0130 | abstract (methods timing 20 min per page text) | EXT | post-timing ambiguity |
| 7 | Kons RL et al. Effects of multiple judo bouts… countermovement jump metrics. J Hum Kinet | DOI 10.5114/jhk/202147; year unresolved | abstract | EXT | height vs impulse; power/force unchanged |
| 8 | Serrano-Huete V et al. Variability of strength production during a judo contest. Phys Act Rev 2023;11(1):1-10 | DOI 10.16926/par.2023.11.01 | abstract | EXT | immediate post change |
| 9 | Barbas I et al. Greco-Roman wrestlers, one-day tournament. 2011 | DOI 10.1007/s00421-010-1761-7; journal name not on page | abstract (repository) | EXT (amateur wrestling) | context only |
| 10 | Sánchez-Sixto A, Harrison AJ, Floría P. Larger countermovement increases the jump height of CMJ. Sports 2018;6(4):131 | DOI 10.3390/sports6040131 | full text | GEN | depth |
| 11 | Harman EA et al. The effects of arms and countermovement on vertical jumping. Med Sci Sports Exerc 1990;22(6):825-833 | no DOI on retrieved page | abstract | GEN | hands on hips |
| 12 | Time-of-day neuromuscular performance, team-sport athletes: SR/MA (2025) | PMC11782285; authors/DOI unresolved (Frontiers URL 10.3389/fspor.2024.1466050 appeared in the same search but was not matched to this record) | abstract (repository record; PMC page not fetchable) | GEN/EXT | time-of-day covariate |
| 13 | Esteban-García P et al. Static or dynamic stretching in warm-up… jump height and ROM: SR/MA. Appl Sci 2024;14(9):3872 | DOI 10.3390/app14093872 | abstract | GEN | warm-up record/standardise |
| 14 | Ruf L et al. Concurrent validity of CMJ and SJ height, contact mat vs force platform, soccer. Front Sports Act Living 2024;6:1437230 | DOI 10.3389/fspor.2024.1437230 | full text | GEN | method not interchangeable (3.2 cm) |
| 15 | iPhone-app validity/reliability for vertical jump (Balsalobre-Fernández et al., 2015, per my attribution) | St Mary's repository eprint 1715; **journal/DOI/author list unresolved on retrieved material** | full-text excerpt (ICC 0.997; mean diff 1.1 ± 0.5 cm) | GEN | simple-system agreement |
| 16 | Glatthorn JF et al. Validity and reliability of Optojump photoelectric cells for estimating vertical jump height. J Strength Cond Res 2011;25(2) | DOI 10.1519/JSC.0b013e3181ccb18d; PMID 20647944 | abstract/metadata | GEN | simple-system agreement |
| 17 | Claudino JG et al. The countermovement jump to monitor neuromuscular status: a meta-analysis. J Sci Med Sport 2017;20(4):397-402 | DOI 10.1016/j.jsams.2016.08.011; PMID not shown | abstract (repository) | GEN | mean (average) CMJ height detected fatigue/supercompensation better than peak |
| 18 | Cormack SJ et al. Reliability of measures obtained during single and repeated countermovement jumps. Int J Sports Physiol Perform 2008;3(2):131-144 | DOI 10.1123/ijspp.3.2.131 | metadata (citation only today; abstract read in an earlier pass) | GEN | CMJ reliability (general) |
| 19 | Cormack SJ et al. Neuromuscular and endocrine responses of elite players during an Australian rules football season. IJSPP 2008;3(4):439-453 | DOI 10.1123/ijspp.3.4.439 | abstract (repository) | EXT | flight:contraction time fell in fatigue periods |
| 20 | Gathercole RJ et al. Alternative countermovement-jump analysis to quantify acute neuromuscular fatigue. IJSPP 2015;10(1):84-92 | DOI 10.1123/ijspp.2013-0413; authors not shown on the page retrieved | abstract | GEN/EXT | flight time, mean power, peak velocity changed beyond variability; **abstract does not mention time to take-off or FT:CT** |
| 21 | Anicic Z et al. Assessment of countermovement jump: what should we report? Life 2023;13:190 | DOI 10.3390/life13010190 | abstract (repository) | GEN | 3 trials/session; performance variables most reliable (CV 4.2–11.1%) |
| 22 | Alba-Jiménez C, Moreno-Doutres D, Peña J. Trends assessing neuromuscular fatigue in team sports: a narrative review. Sports 2022;10:33 | DOI 10.3390/sports10030033 | **metadata only** (page body/abstract not available) | GEN | NOT used for any decision (see §9 correction) |
| 23 | Hopkins WG. Measures of reliability in sports medicine and science. Sports Med 2000;30(1):1-15 | DOI 10.2165/00007256-200030010-00001 | metadata | GEN | reliability framework (typical error) |
| 24 | Blazevich AJ, Babault N. PAP vs PAPE in humans. Front Physiol 2019;10:1359 | DOI 10.3389/fphys.2019.01359 | full text (truncated at references) | GEN | PAPE onset ~6–10 min, may last >15 min |
| 25 | Seitz LB, Haff GG. Factors modulating PAP of jump, sprint, throw, and upper-body ballistic performances: SR/MA. Sports Med 2016;46(2):231-240 | DOI 10.1007/s40279-015-0415-7 | metadata (earlier abstract read) | GEN | PAPE context |
| 26 | Tillin NA, Bishop D. Factors modulating PAP and its effect on subsequent explosive activities. Sports Med 2009;39(2):147-166 | DOI 10.2165/00007256-200939020-00004 | metadata (earlier abstract read) | GEN | PAPE context |
| 27 | Rampinini E et al. Match-related fatigue in soccer players. Med Sci Sports Exerc 2011;43(11):2161-2170 | DOI 10.1249/MSS.0b013e31821e9c5c; PMID 21502891 | abstract | EXT | context only; **abstract reports no CMJ** (see §9 correction) |
| 28 | Chang C-C et al. Effect of acute judo training on CMJ and perceived fatigue, collegiate athletes. IJERPH 2022;19(24):17008 | RePEc handle RePEc:gam:jijerp:v:19:y:2022:i:24:p:17008-:d:1007108; DOI not shown on page | abstract (RePEc) | EXT | immediate vs 24 h; FT:CT and contraction durations at 24 h |
| 29 | Assessing post-competition recovery in judo. Res Sports Med 2025;33(4):448-457 | DOI 10.1080/15438627.2025.2471384; authors unresolved | abstract (aggregator) | EXT | CMJ may stay unchanged in judo competition |
| 30 | CMJ vs countermovement rebound jump, NCAA Division I football. J Strength Cond Res 2026 | authors/DOI unresolved | abstract (aggregator) | EXT | higher load linked with impaired recovery of CMJ RSImod and time to take-off. **Candidate #2 is not reopened; the rebound-jump test is noted only.** |
| 31 | Dei LL et al., Shean J et al., BMJ OSEM ACL qualitative, St Cloud ethnography | see §5 | see §5 | DIR (not CMJ) | gap-search screening only |
| 32 | Bell J et al. Injury incidence and prevalence in wrestlers based in Britain. J Elite Sport Perform 2023;3(1):1-13 | DOI 10.54080/KSMO2842 | full text | EXT (amateur) | excluded; amateur, not professional |

Blocked/unavailable: PMC9778897 (reCAPTCHA), PMC10936519 (reCAPTCHA), PMC10463540 (reCAPTCHA), PMC6316300 (reCAPTCHA, content obtained instead via a repository copy of the same paper, row 10), PMC11782285 and PMC8950744/PMC9865236 on pmc.ncbi.nlm.nih.gov (allowlist), Thieme-Connect 10.1055/a-2558-7555 (bot-protection), direct PubMed/Europe PMC/Crossref/OpenAlex/Semantic Scholar (403), PubMed page 29098658 (reCAPTCHA; identifiers confirmed from a repository record instead).

## 9. Remaining unresolved evidence issues, and corrections to the ANA40 audit

Corrections found while recovering identifiers (none changes an approved decision; each narrows what the evidence supports):
1. **Rampinini 2011** was cited in ANA40 (§10) alongside PAP/PAPE and "immediate" timing. Its abstract reports MVC, sprint, soreness, voluntary activation, EMG and stimulation responses; it reports **no CMJ**. It should be read as general soccer-fatigue context, not CMJ or PAPE evidence.
2. **Gathercole 2015** was cited in ANA40 (§4) for time-to-take-off reliability/sensitivity. The abstract retrieved today names flight time, mean power, peak velocity, force at zero velocity and force-velocity area, and **does not mention contraction time or FT:CT**. Support for time to take-off therefore rests on Cormack 2008b (flight:contraction time fell in fatigue periods), Marqués-Jiménez 2025 (longer propulsive phase post-match in starters), Chang 2022 (FT:CT lower and eccentric/concentric/total durations longer at 24 h) and the 2026 NCAA abstract. All are EXT and abstract-level. **Reliability of time to take-off has not been verified from a source I read** (Anicic 2023 reports reliability by metric class, not time to take-off specifically in the page text retrieved). It is a pilot-derived item.
3. **Claudino 2017** (abstract read directly today): average CMJ height detected fatigue and supercompensation better than peak height. This strengthens the mean-of-trials choice beyond what ANA40 stated.
4. **Alba-Jiménez 2022**: only metadata was retrievable; ANA40 listed it with Claudino as support for averaging. It should not be counted as support for mean-vs-best. Averaging support now rests on Claudino 2017 alone (plus Anicic 2023 for a 3-trial design, whose mean-vs-best handling is not stated on the page).
5. **Anicic 2023** (Life 13:190) was labelled "Anicic 2023" in ANA40; identifier now recovered. The paper reports 79 adults, 3 maximal CMJs per session, two visits 24–48 h apart.
6. **Immediate-post timing** gets additional ambiguity from Chang 2022 (fatigue detected at 24 h but not immediately after judo training) and from the judo competition study (CMJ unchanged at 24/48 h). These are consistent with leaving the post-window and the 24/48 h usefulness pilot-derived.
7. **Cormack 2008b** in ANA40 referred to the AFL-season paper (IJSPP 3(4):439-453), not the single-match paper.

Still unresolved: authors/DOI for the time-of-day meta-analysis (PMC11782285); DOI/journal/authors of the iPhone-app validity paper; authors/DOI of the 2026 NCAA CMJ/CMRJ abstract and of the 2025 judo competition paper; year of Kons; abstract-level only (not full text) for most support; verbatim strings of ~16 earlier-session queries lost; one Thieme record unscreened; no direct PubMed/Europe PMC/Scopus/WoS/SPORTDiscus search; no preprint-server search beyond general web search.

## 10. Freeze-status recommendation

The CMJ decisions that the reviewer approved are not weakened by anything found: no direct evidence contradicts them, and the corrections in §9 narrow support for time to take-off (already conditional and pilot-checked) and for averaging (now rests on Claudino 2017). The professional-wrestling gap wording in §7 is the strongest defensible. The database-grade search requested in Task 1 was not achievable here; the replication strings in §4F should be run by someone with database access if the novelty claim is ever relied on externally. Pilot-derived items remain pilot-derived.

EVIDENCE FREEZE READY WITH DOCUMENTED LIMITATIONS
