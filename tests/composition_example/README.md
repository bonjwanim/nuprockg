# The same case in a composition of existing vocabularies and in NuProc 0.9.0

*Existing event and role models plus PROV-O and a small extension could do the same, so what concrete reason is
there to use NuProc?* This folder answers with one synthetic case expressed twice — once with the
strongest composition of existing vocabularies we could build, without any NuProc term, and once in NuProc 0.9.0 —
and with the same three questions, the same four constraints and the same broken variants run on both. Every number
below is taken from `results/summary.txt` and the CSV files beside it, which `run.py` rebuilds from the files in this
folder.

## 1. The case (synthetic; every label carries "(SYN)")

| | Engagement A | Engagement B |
|---|---|---|
| What happened | the export side meets the host government's ministry, March 2024, in *Demo case (SYN)* | a second engagement in the same case, May 2024 |
| Reports | two news records, clustered into one event | one news record |
| Export-side actor as reported | the bundled label *Vendor K / Utility K (SYN)*, which names two candidate organisations; the evidence does not say which one: the reference stays **unresolvable (candidate set)** | *Vendor Beta (SYN)*, resolved to that organisation |
| Host side | the host government (counterparty role), no organisation identified | the same |
| Final role claims | technology supply, construction contract (model coding v3) | **technology supply, financing** — two claims by a model coding activity that followed two plans (codebook v3.0, prompt specification v3) |
| Earlier claims | none | a model first pass (commercial supply), a human coder A (construction contract), and an adjudication that revised the first pass (technology supply) |

Questions (SPARQL, both encodings): **Q1** Which organisations could the actor of engagement A be, and is it resolved?
**Q2** Which roles did Vendor Beta take in engagement B, which claim is final for each, which activity and plans
produced it, and which earlier claims disagree? **Q3** In which engagements did an organisation take two or more roles?

Constraints (SHACL, both encodings): **c1** a candidate-set reference names at least two candidates and is not marked
resolved; **c2** every role value on a participation has exactly one final claim that agrees with it; **c3** a coding
activity has a qualified association per plan, and a model activity has a prompt-specification plan; **c4** a role's
bearer participates in the engagement that realizes it.

## 2. The composition chosen, and why

| Element of the case | Composition (`composition.ttl`) |
|---|---|
| Procurement case, engagements, month | `sem:Event`, `sem:subEventOf`, `sem:hasTimeStamp "2024-03"^^xsd:gYearMonth`, `sem:eventType` |
| News records and what they report | `gaf:Mention` with `gaf:denotes` → the engagement; `prov:wasDerivedFrom` → article; `prov:wasGeneratedBy` → extraction activity. As in NewsReader, the two records denote one event: the event *is* the cluster |
| Side of an engagement, participant | one `sem:Role` constraint node per side, value of the engagement's `sem:hasActor`; `rdf:value` → the actor only when it was identified; the side is a `sem:roleType` value |
| Several roles | further `sem:roleType` values on the same node (SEM puts no cardinality on `sem:roleType`) |
| Actor reference | `gaf:Mention` ("Mentions are references to members of the gaf:Instance class") with `prov:value` (the label as found); a resolved mention `gaf:denotes` the organisation |
| Candidate set, resolution status, link participation → reference | **ad hoc**: `ex:candidate`, `ex:resolutionStatus`, `ex:actorReference` |
| Role claim | `rdf:Statement` (RDF reification): `rdf:subject` the participation node, `rdf:predicate sem:roleType`, `rdf:object` the claimed role type |
| Who claimed it, following which plans | `prov:wasGeneratedBy` → `prov:Activity`; one `prov:qualifiedAssociation` per plan (`prov:agent`, `prov:hadPlan`); `prov:SoftwareAgent` / `prov:Person`; plan type by `dcterms:type` |
| Adjudication | `prov:wasRevisionOf` → the revised claim; `prov:wasInformedBy` between the activities |
| Which claim is final for each value | the participation node `prov:wasDerivedFrom` its final claims (PROV: derivation is "the construction of a new entity based on a pre-existing entity") |
| Organisations, codes | `org:Organization` (W3C ORG) and `sem:Actor`; SKOS concept schemes for role types, sides, counterparty role, statuses, plan types |

**Why this composition is the strongest we found.** It follows the term-level comparison of the paper (Table S1 and
Section S2 of the supplementary material), which rates SEM *reuse by composition* for roles and several role types, PROV-O *reuse as-is* for claim provenance,
revision and plans, and GAF as a news-domain separation of mentions from what they denote. It is built to
need as few new terms as possible: claims need none (RDF reification), finality needs none (PROV derivation), plan
types need only codes, several roles need none. Two of the three gaps are those the term map found in all ten resources:
no term for a reference known to denote one of several candidate organisations, and no resolution-status term. The
third is the link from a participation to its mention, which SEM and GAF do not provide (section 3). Every
published term the two encodings use (49) is declared in its vocabulary (`check_terms.py` → `results/term_check.csv`).

**Considered and not used** (facts in `results/term_check_considered.csv`):

- *ePO `epo:AgentInRole` (core 5.2.0).* It "ties an Agent to a part they play in a given Situational Context", but its
  context property `epo:contextualisedBy` ranges over `epo:ProcurementElement` (a procedure, a lot), not an engagement
  event; its kinds of role are classes (`epo:OfferingParty`, `epo:AcquiringParty`, `epo:Tenderer`, …) with no
  role-type property, so the six role types would be six ad-hoc subclasses; and `epo:playedBy` has cardinality 1 on
  `epo:AgentInRole`, so a role whose agent is one of two candidates is incomplete by ePO's own axiom. ePO's
  `OfferingParty` / `AcquiringParty` are the closest published counterpart of NuProc's two sides, within a
  procurement process.
- *W3C ORG roles* (`org:Membership`, `org:Role`) are roles of an agent *in an organisation*, not in an event.
- *CIDOC CRM* (`PC14_carried_out_by` with `P14.1_in_the_role_of`; `E13_Attribute_Assignment` for claims): P14 implies
  causal or legal responsibility, E13 is the act of assigning rather than the claim it produces, and CIDOC has no
  revision relation, so PROV-O would still be needed.
- *SEM views* (`sem:View`, `sem:accordingTo`) — SEM's own idiom for conflicting role views. A view hangs on the
  engagement as one more `sem:hasActor` value, so every participant query must exclude views, and a view has no
  activity or plan, so PROV-O would still be needed.
- *`rdf:Alt` for the candidate set*: RDF Schema 1.1 says "the first member of the container … is the default choice",
  which would rank one candidate above the other. *`owl:oneOf`*: an anonymous participant typed by
  `[owl:oneOf (K UtilityK)]` states "one of these" in OWL, but needs a blank-node participant, an `rdf:List` in every
  query and shape, and still has no place for the status.
- *`gaf:denotedBy` from the participation to the mention*: the participation node is not what the mention denotes.
  *`prov:wasDerivedFrom` for the same link* would overload the property that marks final claims.
- *Wikibase ranks* (`wikibase:PreferredRank`) for finality: `wikibase:rank` has the domain `wikibase:Statement`; PROV
  derivation needs no borrowed domain. *Named graphs / nanopublications* for claims: SHACL 1.0 validates a data graph,
  so a rule relating a claim held in its own graph to the participation in another needs more than the shapes used
  here. *RDF 1.2 triple terms*: rdflib 7.6 does not parse them (checked), and pySHACL 0.40.1 does not validate them.

## 3. Ad-hoc terms the composition needs (`composition_ext.ttl`)

| Term | Kind | Why no published term |
|---|---|---|
| `ex:actorReference` | property, `sem:Role` → `gaf:Mention` | SEM puts the actor itself under `rdf:value`; GAF links a mention to what it denotes, not to the participation it was used in |
| `ex:candidate` | property, `gaf:Mention` → `org:Organization` | *candidate-set reference*: absent in all ten resources of the term map |
| `ex:resolutionStatus` | property, `gaf:Mention` → `skos:Concept` | *resolution status*: no status term in any of them |

Plus the builder's code lists (15 concepts in 6 schemes, 72 lines): role types (6), sides (2), counterparty role (1),
statuses (3), plan types (2), engagement type (1). NuProc ships the corresponding schemes, with definitions, scope
notes and examples, in `ontology/nuproc-codebook.ttl`. A builder could drop `ex:resolutionStatus` and read "resolved"
from the presence of `gaf:denotes`; the graph could then no longer tell *unresolvable* from *not yet resolved*.

## 4. Results

Triple counts are per section of the two data files (`results/representation.csv`; every triple belongs to one
section; the sections are marked in the files). The candidate-set row counts section P1, which holds both actor
references (the candidate set of A and the resolved reference of B); the claims row counts P2 (claims, final-claim
links, activities, associations, agents, plans); the roles row counts P3. Shape sizes count the non-blank, non-comment lines of each named shape
and the triples of its description (`results/shapes_size.csv`). Query counts are triple patterns as written,
including those inside `EXISTS` (`results/query_metrics.csv`).

| | Phenomenon | Composition | NuProc 0.9.0 |
|---|---|---|---|
| **Represent** | Candidate set | 11 triples; `gaf:Mention`, `gaf:denotes`, `prov:value` + **3 ad-hoc properties** + 2 builder-defined status codes | 31 triples; 21 NuProc terms (`AmbiguousOrganizationReference`, `hasCandidateOrganization`, `hasResolutionStatus`, `resolvedTo`, `ResolutionClaim`, `hasFinalResolutionClaim`, …) + 2 codebook codes; no ad-hoc term; 19 of the triples are the two references' resolution claims and the activity that made them |
| | Divergent claims | 99 triples; claim = `rdf:Statement`, 5 triples; final = `prov:wasDerivedFrom`; 0 ad-hoc terms; plan type as a `dcterms:type` code | 93 triples; claim = `RoleClaim`, 4 triples; final = `hasFinalRoleClaim`; plan types are classes (`CodebookVersion`, `PromptSpecification` ⊑ `prov:Plan`) |
| | Multiple roles | **4 triples**: two `sem:roleType` values per participation node; 0 ad-hoc terms | 19 triples: 4 coded values (`hasEngagementRole`) + the real-world layer for the resolved participant: participation (`RO_0000057`), 3 role individuals in the case (`RO_0000081`, `concernsCase`, `BFO_0000054`), 2 `supportedByClaim` |
| **Validate** | Candidate set (c1) | builder writes **1 shape, 14 lines**; base conforms; c1a (one candidate) and c1b (marked resolved) caught | ships 5 shapes, 166 lines; base conforms; c1a caught by `AmbiguousReferenceCandidateShape`, c1b by `ReferenceKindStatusShape`, `ActorReferenceShape` and `ResolutionClaimShape` (the reference no longer matches its final resolution claim) |
| | Divergent claims (c2, c3) | builder writes **4 shapes, 78 lines**; c2a (value without final claim), c2b (disagreeing earlier claim marked final), c3a (two plans on one association), c3b (model without prompt plan) all caught | ships 5 shapes, 120 lines; the same four caught (`CodedParticipationRoleClaimShape`; c3a by `CodingActivityShape`, c3b by the profile shape `CodingActivityProfileShape`) |
| | Multiple roles (c4) | builder writes **1 shape, 7 lines**: in SEM a role and the participation are one node, so the bearer participates by construction; c4 (node detached from its engagement) caught | ships 2 shapes, 154 lines; c4 (bearer not a participant) caught by `EngagementShape` |
| **Query** | Q1 | answered: Utility K (SYN), Vendor K (SYN); `unresolvable_candidate_set`; not resolved. 10 patterns, 3 on ad-hoc terms | same answer; 11 patterns (one more hop: engagement → cluster → participation) |
| | Q2 | answered: final technology supply and financing (Role coding v3, Coding model M3, Codebook v3.0 + Prompt specification v3); earlier and disagreeing: commercial supply (first pass, revised by the adjudication) and construction contract (human coder A). 19 patterns, 8 join variables, 2 `EXISTS` | same answer; 19 patterns, 11 join variables, 2 `EXISTS` |
| | Q3 | answered: engagement B, Vendor Beta (SYN), 2 roles. 7 patterns | same answer; 7 patterns (real-world layer) |

Totals: composition 184 triples, NuProc 270 (NuProc also keeps the two clusters, their clustering rule, their
identification and occurrence status with the claims behind them, and month instants, 121 triples in S0 against 61,
and the resolution claims of the two references in P1). The builder of the composition writes **6 shapes (99 lines)**,
**3 ad-hoc terms (15 lines)** and **72 lines of codes** — 186 lines in all — before the first validation; a NuProc
user writes none. The 12 NuProc shapes that implement c1–c4 (440 lines) are a part of the 47 named shapes shipped in
`ontology/nuproc-shapes.ttl`, all of which run on `nuproc.ttl` with no violation and no warning.

Validation detail (`results/validation.csv`): both base graphs conform; each of the seven broken variants per encoding
is caught by the shapes of its own constraint and by no other shape. The broken variants are SPARQL updates in
`broken/`, applied in memory.

## 5. What the composition does as well as NuProc

- **It can say and check all three phenomena.** With three ad-hoc properties it represents the candidate set, and Q1–Q3
  return the same rows from both encodings. The shapes its builder writes catch every broken variant that NuProc's
  shipped shapes catch.
- **Claim provenance is the same PROV-O chain.** NuProc reuses PROV-O for activities, agents, qualified associations,
  plans and revision; the composition reaches the same answers to Q2 with the same number of triple patterns, and
  needs no new term for claims (RDF reification) or finality (PROV derivation).
- **Several roles are shorter in SEM.** `sem:roleType` takes several values on one node: 4 triples against NuProc's 19,
  which states the roles twice (coded values on the participation, and role individuals in the real-world layer). For
  the same reason c4 holds by construction in the composition and needs a 7-line shape, where NuProc needs a SPARQL
  rule that keeps the participant (`RO_0000057`) and the role bearer (`RO_0000081`) in step.
- **Q1 is one hop shorter** in the composition, because its participation hangs on the engagement directly.

## 6. What NuProc adds here

- **Published terms where none exist.** For the candidate set and the resolution status the composition has only
  private ad-hoc terms; NuProc publishes them with definitions ("At least two: with one candidate the reference is
  resolved, not ambiguous") and axioms (an actor reference is disjoint from an organisation). A second builder would
  mint different `ex:` terms, and the two datasets would share neither queries nor shapes.
- **Shipped constraints.** The four constraints are already written and come with more: the reference kind decides
  the admissible statuses (five kinds, four statuses), `resolvedTo` is present exactly when the status is resolved, a
  candidate organisation and its own name count as one candidate, a role is identified by bearer, case and kind
  and agrees with its final claims, and side roles come from a resolved participation on that side.
- **What was reported and what happened stay apart.** In the composition the event is at once what the two records
  denote (the cluster) and where the roles belong, there is no node for the cluster or its clustering rule, and the
  participation node is read both as SEM's constraint on the event's actor and as a record derived from claims. NuProc
  keeps the cluster (with `clusteredBy` → the month rule), the records and the coded participations as information
  entities that report a separate `Engagement`, and asserts real-world roles only for the resolved participant.
  None of the three questions needs this separation; it is what the 19 triples for roles pay for.
- **Typed plans**: `CodebookVersion` and `PromptSpecification` are classes, where the composition types plans with a
  code (`dcterms:type`), so its c3 shape depends on the builder's code IRI.

## 7. Limits

- One synthetic case with two engagements; the counts describe this case, not datasets in general.
- Q1-Q3 and c1-c4 do not read the occurrence, identification and resolution claims; section 9 does.
- The composition was built by the same agent that wrote the NuProc encoding. It was built to need as few new terms
  as possible and the alternatives above were weighed, but another builder could compose differently (CIDOC CRM and
  PROV-O, nanopublications), and the counts would differ.
- Line and triple counts measure size, not difficulty or correctness; the NuProc shapes counted for c1–c4 also check
  more than c1–c4.
- No reasoner was run; the OWL axioms (disjointness, cardinality restrictions) are not exercised here.
- **TBox version.** `run.py` reads the NuProc modules from the `ontology/` folder of the repository (TBox 0.9.0);
  `results/inputs.csv` records the sha256 of every module it read.
- pySHACL's `ont_graph` argument is not used: in pySHACL 0.40.1 it copies only RDFS and OWL axioms into the data
  graph, not the codebook's SKOS concepts, so every check that reads a code's scheme or role class fails (17
  violations on `nuproc.ttl`, all of that kind); and its full-mixin switch (`PYSHACL_USE_FULL_MIXIN`) fails with
  rdflib 7.6. `run.py` merges the vocabulary files into the data graph instead.

## 8. Files and how to re-run

| File | Content |
|---|---|
| `composition.ttl` | the case in the composition (184 triples) |
| `composition_ext.ttl` | the builder's ad-hoc terms (section X1) and code lists (X2) |
| `composition_shapes.ttl` | the builder's SHACL for c1–c4 |
| `nuproc.ttl` | the case in NuProc 0.9.0 (270 triples) |
| `composition_q1.rq` … `nuproc_q3.rq` | Q1–Q3 for each encoding |
| `broken/*.ru` | seven broken variants per encoding (SPARQL updates) |
| `run.py` | rebuilds `results/` (deterministic; Python 3.14.3, rdflib 7.6, pySHACL 0.40.1) |
| `check_terms.py`, `vocabularies.csv` | checks every published term against its vocabulary file (addresses and sha256 in the CSV; the files are not redistributed) |
| `status_claims/` | the extension of section 9, with its protocol, files, runner and results |
| `results/` | `representation.csv`, `terms_used.csv`, `validation.csv`, `validation_details.csv`, `shapes_size.csv`, `q*_*.csv`, `query_metrics.csv`, `term_check*.csv`, `inputs.csv` (sha256 of every input), `summary.txt` |

```bash
python run.py                      # from this folder or anywhere; reads the NuProc modules from the repository
python -P check_terms.py --fetch DIR   # downloads the vocabularies into DIR (generic User-Agent, no contact data)
```


## 9. Extension: the status claims and the assertion rule

Q1-Q3 and c1-c4 do not read the occurrence and identification status of a cluster, the claims behind a resolution, or
the rule for what is asserted about the real world. `status_claims/` adds three report groups (a planned meeting, two
meetings of one month that the key joined, and a meeting whose identification and reference a person revised), three
questions (Q4-Q6), four constraints (c5-c8) and seven broken variants per encoding. `status_claims/PROTOCOL.md`, with
the expected answers, was fixed before either encoding of the new material was written, and its checksum is compared
at every run. A separate language-model instance wrote the composition's part from the protocol, the base composition
and the published vocabularies, without sight of the NuProc encoding of the new groups or of NuProc's shapes; its
choices and the alternatives it rejected are in `status_claims/COMPOSITION_NOTES.md`.

| | Composition | NuProc 0.9.0 |
|---|---|---|
| Whole case (data files) | 487 triples | 486 triples |
| New ad-hoc terms | none: `schema:eventStatus` and `adms:status` are borrowed for the two statuses | none |
| New codes | 6 (30 lines) | none |
| Shapes for c5-c8 | builder writes 4 (163 lines) and rewrites 2 base shapes (58 lines), so that 10 shapes (281 lines) are in force | 10 shipped (507 lines), which also check more |
| Seven broken variants | all caught by the shapes of their own constraint, and by no other | all caught by the shapes of their own constraint (c7b also by `CodedParticipationReferenceCoherenceShape`) |
| The parent folder's seven broken variants, on the extended composition | all still caught | not re-run: no NuProc shape changed |
| Q4-Q6 | the protocol's rows; 31 triple patterns | the protocol's rows; 40 triple patterns |

So the composition can state and check this material too, with no further ad-hoc property, and at about the same size.
What the numbers do not show:

- **The two status properties are stretched.** ADMS defines `adms:status` as "the status of the Asset in the context of
  a particular workflow process", and a report group is no asset. The five published values of `schema:eventStatus` do
  not separate a meeting announced for later from one that took place, so the values are the builder's.
- **The composition keeps no engagement apart from its reports.** Its planned group C and its merged group D are
  `sem:Event`s like the others. No statement says that a group reports an engagement: the rule (occurred and not
  merged) is written in the shape and again in Q4, and any query for the set of engagements has to repeat it. In NuProc
  the rule is applied when the graph is built and checked by the shipped shapes, and queries read the real-world layer.
- **In one respect the composition keeps more.** The candidates of the revised judgement of group E stay as reified
  statements. NuProc keeps that claim's status and the label, but not its candidates, because
  `hasCandidateOrganization` belongs to an ambiguous reference and the reference is typed by its final claim.
- **A claim that resolves a reference** takes two reified statements in the composition (status and organisation) and
  one node in NuProc, so section R is the largest difference in triples: 76 against 48.

The limits of section 7 apply: one synthetic case, and every encoding written by a language model.

```bash
python status_claims/run.py                       # rebuilds status_claims/results/
python -P status_claims/check_terms.py --fetch DIR   # checks the published terms the extension uses
```
