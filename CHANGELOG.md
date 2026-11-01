# Changelog — NuProc Ontology

The four modules (core, codebook, alignments, shapes) are versioned together under semantic versioning; a
module with no change of its own still moves to the new version. Versions 0.1.0 to 0.8.0 were frozen during
development and not released. Their files are available on request (see *Earlier versions* in the README), as
are the design records cited below by number (ADR-NNNN).

## 0.9.0 — 2026-10-29

First public release.

- **Occurrence status** (ADR-0041). New SKOS vocabulary `OccurrenceStatus` (*occurred*, *planned*, *denied*,
  *unclear*) and property `hasOccurrenceStatus` (at most one per cluster). Each value has one final
  `OccurrenceClaim`, with `occurrenceClaimAbout`, `claimedOccurrence` and `hasFinalOccurrenceClaim`. The
  occurrence status is kept apart from the identification status.
- **Resolution claims** (ADR-0043). Each judgement of how an actor reference is resolved is a `ResolutionClaim`,
  with `resolutionClaimAbout`, `claimedResolutionStatus`, `claimedResolvedTo` and `hasFinalResolutionClaim`. The
  status and `resolvedTo` of a reference are those of its final claim; claims that were not adopted remain.
- **Identification claims** (ADR-0044). Each judgement of what a cluster's identification with one engagement
  rests on (the clustering key alone, a person's check, or a person's finding that it merges engagements) is an
  `IdentificationClaim`, with `identificationClaimAbout`, `claimedIdentification` and
  `hasFinalIdentificationClaim`; the identification status of a cluster is that of its final claim.
- **Procurement case** (ADR-0044). `ProcurementCase` ⊑ BFO process: the procurement for one new-build project,
  which the research design chooses to study; an engagement concerns one case.
- **`namesParticipant`** (ADR-0044). The property from a coded participation to the organisation it names, called
  `hasParticipant` in 0.8.0, has a new IRI, apart from RO's *has participant*; there is no alias.
- **Real-world layer.** The axiom that every record reports an engagement was removed, so the report of a
  planned or denied engagement does not imply that it took place. Only an unmerged cluster whose final status
  is *occurred*, and its records, report an engagement; only a cluster whose final status is *occurred* grounds
  a role or a side role (the claims of a merged cluster support a role but yield no realization).
- **Consortia.** A group acting as one party, such as a consortium, is one organisation, identified as a
  collaboration rather than by its members; `org:hasMember` (declared in core) names the members.
  The cap of one participant per coded participation, and of one resolution target per reference, is back in
  the pattern layer.
- **SHACL.** Occurrence-status constraints on `EngagementClusterShape` and a new `OccurrenceClaimShape`. Three
  gaps were closed: records of a cluster that reports no engagement, the qualified association of the activity
  behind a final claim, and an engagement that no cluster reports. A new `ResolutionClaimShape` checks resolution
  claims and that a reference's final claim agrees with it; in the profile, every NuProc reference has a final
  resolution claim (`ActorReferenceProfileShape`). A count stated by a collective reference is at least two. The
  rules for what the real-world layer asserts (`EngagementShape`, `EngagementRoleShape`) are of a third rule kind,
  *assertion rule*, still `sh:Violation`. A new `IdentificationClaimShape` checks identification claims and that a
  cluster's final claim agrees with it; in the profile, every NuProc cluster with an identification status has a
  final identification claim. 47 named shapes (20 pattern, 27 profile).
- **Disjointness.** The large `owl:AllDisjointClasses` axiom now covers seventeen classes (codebook versions,
  prompt specifications, quality measurements, the clustering rule, and occurrence, resolution and identification
  claims were added), and the real-world classes are disjoint with the coding and validation activities.
- **`OrganizationType`.** `Unknown` was removed, as decided for 0.3.0 (ADR-0025): the state it named is the
  classification status *undetermined*, and no organisation used the value.
- **Labels.** `BFO_0000054` is labelled *has realization*, as in BFO-2020 (*realized in*, RO's label, is its
  alternative label), and the participant property *names participant*, apart from RO's *has participant*.
- **Definitions** revised: `Organization`, `ProcurementCase`, `namesParticipant`, `hasEngagementIdentification`,
  `reportsEngagement`, `supportedByClaim`, `wasGeneratedBy`,
  `hasResolutionStatus`, `resolvedTo`, `BFO_0000054`,
  `AmbiguousOrganizationReference`, `DefiniteOrganizationReference`, `RoleClaim`, `hasEngagementRole`,
  `claimedRole`, `EngagementRoleCodingActivity`, `CodingActivity`, `CodebookVersion`, `SourceArticle`,
  `measuresProperty`, the `EngagementRoleType`, `CodedPlayerCategory` and `EventType` schemes, `verified`,
  `key_based` and `unresolvable_candidate_set`.
- **Queries.** CQ20 (the provenance of the occurrence status) is new. CQ18 returns the occurrence status of the
  reporting cluster. Three worked examples (G7–G9) show, on the synthetic graph, errors NuProc prevents.

## 0.8.0 — 2026-10-14

- **Real-world layer** (ADR-0040), aligned by IRI to BFO and RO, which are not imported. `Engagement` ⊑ BFO
  process: it concerns exactly one procurement case and has one or more participating organisations (RO *has
  participant*). `EngagementRole` ⊑ BFO role: it is borne by one organisation (RO *role of*) in one procurement
  case and realized (BFO *realized in*) in zero or more engagements of that case. `Organization` ⊑ BFO object
  aggregate. Two side roles (`ExportSideRole`, `HostSideRole`) and six facet roles (technology supply,
  construction contract, financing, state sponsorship, commercial supply, other), pairwise disjoint.
- **Between the layers.** `reportsEngagement` (functional, ⊑ IAO *is about*), `supportedByClaim` (from a facet
  role to the final claims that support it) and the annotation property `roleClass`. `org:subOrganizationOf`
  is declared.
- **Identification status.** New vocabulary `EngagementIdentificationStatus` (*key_based*, *verified*,
  *merged*) and property `hasEngagementIdentification`. The axiom that every cluster reports an engagement was
  removed, since a merged cluster reports no single engagement.
- **Measurements** state the coded values they were computed on (`dqv:computedOn`) and the comparison made
  (`comparisonType`).
- **Renamed, without aliases** (the earlier names were never released). `FunctionClaim` → `RoleClaim`
  (`claimedFunction` → `claimedRole`, `hasFinalFunctionClaim` → `hasFinalRoleClaim`);
  `EngagementFunctionCodingActivity` → `EngagementRoleCodingActivity`; `hasEngagementFunction` (one value) →
  `hasEngagementRole` (several, unordered), with the scheme `engagementfunction` replaced by `engagementrole`;
  `hasDirectionRole` and `directionrole` (Initiator, Counterparty) → `hasSide` and `siderole` (*export_side*,
  *host_side*). The channel rules R1, R3 and R4 now name the export side.
- **SHACL.** Shapes for the real-world layer (`ReportsEngagementShape`, `EngagementShape`,
  `EngagementRoleShape`), for role claims and for qualified associations (`AssociationShape`), and profile
  shapes for role values. The cap of one participant per coded participation moved to the profile layer.
  43 named shapes (17 pattern, 26 profile).
- **Disjointness.** The upper classes of the two layers are declared with `owl:AllDisjointClasses`, and
  engagements are disjoint with coding and validation activities.
- **Queries.** CQ18 (organisations that realize several roles in one engagement) and CQ19 (the claims,
  activities and plans behind a role) are new.

## 0.7.0 — 2026-10-10

- **Renamed, without aliases** (ADR-0039). `EngagementEvent` → `EngagementCluster`, `Participation` →
  `CodedParticipation`, `occursInCase` → `concernsCase`, with the matching shapes. Instance IRIs are unchanged.
- **Claim-level provenance of coded values.** `FunctionClaim` (⊑ `prov:Entity`) with `claimAbout`,
  `claimedFunction` and `hasFinalFunctionClaim`. Each claim is generated (`prov:wasGeneratedBy`) by the
  activity that made it; a claim that adjudication changed is a revision (`prov:wasRevisionOf`) of the
  first-pass claim.
- **SHACL** (pattern layer). An actor reference has exactly one resolution status (before, at most one), and a
  candidate organisation and its name count as one candidate.
- **OntoClean** annotations corrected for `Organization`, `ProcurementCase`, `SourceArticle` and
  `MonthGranularityRule`.
- **IAO.** `EngagementCluster`, `CodedParticipation`, `EventRecord`, `ActorReference` and `FunctionClaim` ⊑ IAO
  *information content entity*, by IRI (not imported).

## 0.6.1 — 2026-10-09

- Annotation-only release; the logic is that of 0.6.0. Internal references were removed from the English
  annotations. The definitions of `hasEngagementFunction`, `hasCounterpartyRole` and their schemes now say that
  the values are coded claims recorded on the participation. Each module declares `owl:priorVersion`.

## 0.6.0 — 2026-09-30

- **Sides without a direction** (ADR-0036). In the pattern layer a participation has at most one direction role
  and names its side by a direction role or by the new data property `sideKey`. An engagement event has exactly
  two participations, which may not share a `sideKey`.
- The definitions of `Participation`, `hasDirectionRole` and the direction-role scheme were made neutral.
  `EventRecord` was generalised to a record of one source item; the requirement that it comes from a news
  article stays in the profile layer.

## 0.5.0 — 2026-09-28

- **Reference resolution** (ADR-0031). `ActorReference` is the superclass of all participant references,
  disjoint with `Organization`, `Participation` and `EngagementEvent`, with a new subclass
  `DefiniteOrganizationReference`. `hasActorReference` links a participation to its reference
  (`hasParticipantReference` ⊑ `hasActorReference`), and `resolvedTo` links a reference to the organisation it
  was resolved to. The domains of `hasResolutionStatus` and `hasSourceMention` were widened to `ActorReference`.
- **Coding plans** (ADR-0033). `CodebookVersion` and `PromptSpecification` ⊑ `prov:Plan`, and a new class
  `EngagementFunctionCodingActivity`. Adjudication is described with PROV terms only.
- **Categories and annotations** (ADR-0032). OntoClean notation follows Guarino and Welty. Korean prose
  annotations are tagged `@ko`, each with an English counterpart.
- **Pattern and profile layers** (ADR-0034). Every named shape belongs either to the pattern layer, for any
  dataset that uses the patterns, or to the profile layer, for the NuProc dataset and codebook (`shapeLayer`,
  `ruleKind`); shapes that mixed the two were split. 31 named shapes (11 pattern, 20 profile).
- **Alignments.** Relations to ePO, ORG and ITS 2.0 were checked against their sources and recorded with
  `rdfs:seeAlso` and editorial notes, without new mapping axioms.

## 0.4.0 — 2026-09-16

- **Host-side participant** (shapes only; ADR-0013, revised). A host-side participation may now name at most one
  participant or participant reference; before, it could name none. The two slots stay exclusive. The other
  modules changed only their version.

## 0.3.0 — 2026-08-21

- **Event-level values apart from participations.** The event-level player role moved to
  `hasSelectedPlayerRole`, so `EngagementEvent` and `Participation` can be declared disjoint.
- **Candidate sets.** A label that names a set of candidate organisations is an
  `AmbiguousOrganizationReference`, not an organisation; unnamed references now come in four kinds.
- **New axis.** `hasEngagementFunction` (six values coded from event evidence) beside the coded player
  category; nine SKOS schemes. A new `TypeClassificationStatus` scheme records the state that `Unknown` in
  `OrganizationType` named (*undetermined*); `Unknown` itself stayed in `OrganizationType`, unused, until 0.9.0.
- **Clustering rule** (ADR-0027): `clusteredBy` and `MonthGranularityRule`. Organisations carry no resolution
  status, each participation belongs to exactly one event, and an ambiguous reference has at least two
  candidates.
- **Build.** The output is deterministic: blank-node identifiers come from the axioms, and `dcterms:modified`
  from the version date.

## 0.2.1 — 2026-08-19

- Metadata-only release; the logic is that of 0.2.0. The shapes module gained the ontology metadata of the
  other modules, and its version annotations were brought in line with theirs. Line endings are fixed to LF,
  so that downloaded files match the checksums.

## 0.2.0 — 2026-08-18

- `OrganizationType` (SKOS): the fixed type of an organisation, assigned in the actor registry and never
  promoted from the coded player category (ADR-0014, ADR-0021).

## 0.1.0 — 2026-08-17

- First version: the OWL modules, SKOS vocabularies and SHACL shapes, generated from the concept registry.
