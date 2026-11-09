# Notes on the status material of the composition

Files: `composition_status.ttl` (data, sections G, O, I, R, W, B0), `composition_status_ext.ttl` (sections X3, X4),
`composition_status_shapes.ttl`, `composition_q4.rq` to `composition_q6.rq` and `broken/` (seven updates).

## 1. Ad hoc terms

None is added. Section X3 is empty and says so in a comment. The ad hoc terms the base already has (`ex:actorReference`,
`ex:candidate`, `ex:resolutionStatus`) are reused without change.

Two of the published properties taken below are looser fits than the others, and the choice is a judgement that a
reader may not share. If either is rejected, one ad hoc property replaces it, with the same shape and query structure:

| Need | Published term used | The stretch |
|---|---|---|
| occurrence status of a report group | `schema:eventStatus` | the values are the builder's codes, because the five published values do not make the distinction (section 3.1) |
| identification status of a report group | `adms:status` | the definition speaks of "the Asset"; only the declared domain, `rdfs:Resource`, admits a report group (section 3.2) |

## 2. New codes (section X4)

Six codes in three schemes, each with a scheme, a notation and a label as in the base:

- `exocc:` occurrence statuses: `planned`, `occurred`.
- `exid:` identification statuses: `key_based`, `merged`, `verified`.
- `exagent:` software agent kinds: `non_model_software` (section 3.7).

The status values must read as the notations `planned`, `occurred`, `key_based`, `merged`, `verified`. No published code
list provides these values with these meanings (sections 3.1 to 3.3), so they are codes.

## 3. What was considered, with the facts relied on

Declarations were read from the files themselves: the local copies for PROV-O, SKOS, RDF, RDFS, DCTERMS, SEM, GAF, ORG,
ePO and Wikibase; on the web for the rest. GRaSP: `ontology/grasp.rdf` at commit
b773cb44167b6ca3253b7b0a7dd9b168d7b39e86 of github.com/cltl/GRaSP. Schema.org:
`https://schema.org/version/latest/schemaorg-current-https.ttl`, and `data/schema.ttl` at commit
7ca5d468ca93485ac00bc3849e2b3baee0b7de0a of github.com/schemaorg/schemaorg. ADMS: `https://www.w3.org/ns/adms.ttl`.

### 3.1 Occurrence status: `schema:eventStatus`, taken

Facts: `schema:eventStatus` is an `rdf:Property` with the comment "An eventStatus of an event represents its status;
particularly useful when an event is cancelled or rescheduled", `schema:domainIncludes schema:Event` and
`schema:rangeIncludes schema:EventStatusType`. `schema:EventStatusType` is "an enumeration type whose instances represent
several states that an Event may be in". Its five published members are `EventCancelled`, `EventMovedOnline`,
`EventPostponed`, `EventRescheduled` and `EventScheduled`, and the comment of `EventScheduled` is "The event is taking
place or has taken place on the startDate as scheduled. Use of this value is optional, as it is assumed by default."

Reading: the property says what is needed, the state of an event. The value set does not: `EventScheduled` covers both a
meeting announced for later and one that took place, and no member says that an event took place. So the property is
published and the values are the builder's, typed `schema:EventStatusType` as the property expects. `domainIncludes` and
`rangeIncludes` carry no entailment; the group is not additionally typed `schema:Event`.

Rejected:

- **GRaSP factuality** (`grasp:hasAttribution`, `grasp:Attribution`, the values in GRaSP's factuality namespace). Three
  reasons. (a) `grasp:hasAttribution` has domain `gaf:Mention`, and `grasp:Attribution` is defined as having some
  `gaf:Mention` through the inverse of that property, so an attribution belongs to one mention. Here the status belongs
  to the report group: group A and group D have two records each and one status, and the group is a `sem:Event`, which
  the records denote. Attaching the status to one record would be arbitrary, and to every record would make one status
  many. (b) The values are closed by `owl:oneOf`: `TemporalValue` is `future`, `non-future`; `CertaintyValue` is
  `underspecified`, `probable`, `possible`, `certain`; `PolarityValue` is `negative`, `positive`. None of them is
  "planned" or "occurred": "occurred" would be three values together (`non-future`, `certain`, `positive`), and new
  values cannot be added to a closed class. (c) The answers must be the notations `planned` and `occurred`, which would
  then exist only as a mapping inside the query.
- **`sem:eventType` with status codes.** SEM's range is `sem:EventType`, "used to classify Events, e.g. meeting". The base
  mixes side codes and role types on `sem:roleType` because all of them are role types; "occurred" is not a kind of
  event. It would also need the status separated from `extype:meeting` by scheme on every read.
- **`dcterms:type`** ("The nature or genre of the resource"): a status is not a nature or genre.
- **DCTERMS, ORG, PROV-O, SKOS, OWL-Time**: no status property. The only status term in ePO is `epo:hasAwardStatus`
  ("whether the lot is awarded, not awarded or still open"), about procurement lots.

### 3.2 Identification status: `adms:status`, taken

Facts: `adms:status` is an `owl:ObjectProperty` with the comment "The status of the Asset in the context of a particular
workflow process.", `rdfs:domain rdfs:Resource` and `rdfs:range skos:Concept`.

Reading: a report group's identification status is its standing in a workflow (formed by the clustering key, then
re-checked to verified or merged). The declared domain admits any resource and the declared range is what the codes
are. The mismatch is the word "Asset" in the comment: a report group is not an ADMS Asset in the sense of that note. It
is disclosed in section 1 for that reason.

Rejected: `schema:eventStatus` (the values are not states of the event but of its identification); an extension of
`ex:resolutionStatus` (its comment and domain are about matching a mention to an organisation); a single generic ad hoc
`ex:status` for both statuses (it would add a term and require a scheme test on every read).

### 3.3 What a group is taken to be, and what is asserted

The base keeps no node for a cluster: "the cluster is the event". Groups C and D therefore keep that convention, and
each is a `sem:Event` even though one is only planned and one joins two meetings. Being a `sem:Event` does not say that
the event happened: the SEM comment is "Events are things that happen. This comprises everything from historical events
to web site sessions and mythical journeys."

Consequence: the graph has no statement that a group reports an engagement. Q4 derives `reportsEngagement` from the two
statuses by the rule that governs what may be asserted: occurred and not merged. The rule is written twice, in
Q4 and in `cs:C8_AssertedParticipationShape`, and the graph cannot say that a group that occurred and is not merged is
nevertheless not taken as reporting an engagement. This is a limit of the composition, recorded here rather than hidden
behind a flag.

Rejected:

- **Typing with `gaf:Instance`.** `gaf:Instance` is equivalent to having some `gaf:denotedBy` mention, so every denoted
  group is an instance, whatever is explicitly typed.
- **A separate cluster node** (for example a `prov:Collection` with `prov:hadMember`) with a link to an event only where
  one is reported. This would reverse the base convention for groups A and B, which must stay as they are.
- **A new event type** `extype:engagement` as the flag: the scheme's concepts are kinds of engagement, so a meeting would
  be an engagement by the scheme itself.
- **An ad hoc `ex:reportsEngagement`**: one more term and one more constraint, restating what the two statuses already
  determine.
- **`sem:View` with `sem:accordingTo`** to scope the coded participations of groups C and D to an authority. It would
  mark coding as an authority's view, but nothing reads that mark, because the assertion is already the presence of
  `rdf:value`.

What is asserted is `rdf:value` on a participation node, the base's form for "the actor". In section W that is one
triple, for group E. Its role type stays in section G with those of groups C and D, and it is read as a role realized by
the organisation because the node has a bearer.

### 3.4 Claims: RDF reification, kept

Status claims are `rdf:Statement`s like the role claims, with the same provenance. `cs:C2_ClaimShape` had to be replaced
for this (section 5).

GRaSP attributions were considered as the claim form and rejected: `grasp:Attribution` is tied to a mention (section
3.1), and would give two forms of claim in one graph.

### 3.5 Final claim: `prov:wasDerivedFrom` from the node, kept

Wikibase's `wikibase:rank` (`wikibase:PreferredRank`, `wikibase:DeprecatedRank`) and `wikibase:BestRank` were considered:
`wikibase:rank` has the domain `wikibase:Statement`, `wikibase:BestRank` is a class of such statements, and either would
add a second mechanism next to the base's. Rejected.

Fact worth keeping in view: `prov:wasRevisionOf` is a subproperty of `prov:wasDerivedFrom` in PROV-O. The final mark is
the derivation from the group or reference node, not from another claim, and PROV-O declares no property transitive,
so a revision does not make the claim it revises final, with or without inference.

### 3.6 Resolution claim: one status statement, plus one organisation statement when resolved

A reified statement holds one triple, and a resolution claim says two things: the status and, when resolved, the
organisation. Following the base's "one claim per (activity, node, value)", the claim is a reified `ex:resolutionStatus`
statement and, when it resolves, a reified `gaf:denotes` statement of the same activity. The status statement is the one
counted as the claim; `cs:C7_ResolutionShape` requires exactly one final status statement, the organisation statement
when resolved, and the same activity for both. Candidates of the earlier claim on group E are reified `ex:candidate`
statements, so the reference itself still names no candidate, which `cs:C1_CandidateSetReferenceShape` requires of a
resolved reference.

Rejected: one node with `rdf:value` for the organisation (it would give `rdf:value` a second meaning beside the bearer of
a participation, and leaves candidates without a form); `ex:candidate` or `gaf:denotes` asserted on the claim node (their
domain is `gaf:Mention`, which a claim is not).

### 3.7 Software that is not a language model

The base shape reads every `prov:SoftwareAgent` as a model. The aggregation pipeline is software and not a model. Typing
it only `prov:Agent` would pass the base shape by hiding what it is, so it is a `prov:SoftwareAgent` with
`dcterms:type exagent:non_model_software`, and the shape is replaced (section 5). PROV-O's `prov:SoftwareAgent` makes no
distinction between kinds of software, and no published class for it was found. The exception is marked on the one
agent, so the rule stays as strong as the base's for every other software agent.

## 4. Departures from the base conventions

1. Claims are no longer only about participations. Occurrence and identification claims are about events, and resolution
   claims about mentions; `prov:wasDerivedFrom` from the node marks the final claims on those node kinds as well.
2. A resolution claim that resolves is two reified statements (section 3.6).
3. `rdf:value` is narrower in meaning than the base comment suggests. The references of groups C and D are resolved, but
   their participation nodes have no `rdf:value`, because no organisation may be asserted for those groups. `rdf:value`
   now means the organisation asserted as actor, not merely one that was identified.
4. The new group nodes are labelled "Report group C (SYN)" and so on, not "Engagement C (SYN)", because groups C and D
   are not taken to report an engagement. Their IRIs follow the base pattern (`syn:engagement-C`).
5. A record of group D denotes the group node, as the base convention has it, although the two records report two
   meetings. The `merged` status records that the key joined them. It is a coded value, as the group is.
6. Two vocabularies join the composition: schema.org and ADMS, one property each (one class as well for schema.org).

## 5. Base shapes replaced

- `cs:C2_ClaimShape_rev` replaces `cs:C2_ClaimShape`. The base shape requires every `rdf:Statement` to be a `sem:roleType`
  claim about a `sem:Role`, which 24 new claims are not. The new shape keeps the cardinalities and the revision rule, and
  checks the subject's class according to the reified predicate: for a role claim it is the same requirement as before.
- `cs:C3_CodingActivityShape_rev` replaces `cs:C3_CodingActivityShape`. The base shape fails on the clustering activity.
  The new shape differs only by excepting agents with the non-model code.

Both are needed to accept the new material; without them the merged graph has violations on those two shapes only.
