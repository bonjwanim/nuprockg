# Status claims and the assertion rule: an extension of the composition example

The base comparison in the parent folder runs three questions (Q1-Q3) and four constraints (c1-c4) on one synthetic
case. None of them reads the occurrence status, the identification status, the resolution claims or the rule for what
is asserted about the real world. This extension adds three report groups, three questions and four constraints that
do, and runs them on both encodings in the same way.

This protocol was fixed, with the expected answers below, before either encoding of the new material was written.

## 1. Rules

- The composition of the new material is written by a separate language-model instance. It is given this protocol, the
  base composition (`composition.ttl`, `composition_ext.ttl`, `composition_shapes.ttl`, `composition_q1.rq` to
  `composition_q3.rq`) and the published vocabularies. It does not see the NuProc encoding of the new material or
  NuProc's shapes.
- The NuProc encoding of the new material is written by the author of this protocol, with the terms and shapes of
  TBox 0.9.0 and no new term.
- The composition uses no NuProc term. It prefers published terms; each ad hoc term is listed with the reason no
  published term fits, and the alternatives considered are recorded.
- The expected answers are not changed once an encoding exists. A question that an encoding cannot answer as expected,
  or a broken variant that its shapes do not catch, is reported as such.
- The shapes for c1-c4 stay in force on the extended graph. If a base shape has to change to accept the new material,
  the changed shape is written in the extension's shapes file and its lines are counted there.

## 2. The new material (synthetic; every label carries "(SYN)")

A *report group* is what the two encodings already hold for engagements A and B: the news records clustered together
under the clustering key, with two sides. Groups A and B stay as they are in the base files. Three groups are added to
the same case, *Demo case (SYN)*. Each has an export side and a host side; the host side is the host government
(counterparty role), with no organisation identified.

| | Group C | Group D | Group E |
|---|---|---|---|
| Month | 2024-06 | 2024-07 | 2024-08 |
| Records and articles | record-C1 from article-C1 | record-D1, record-D2 from article-D1, article-D2 | record-E1 from article-E1 |
| What the group is | a meeting announced for later | two meetings of one month that the clustering key joined | a meeting that took place |
| Export-side label | Vendor Beta (SYN) | Vendor Beta (SYN) | Vendor K / Utility K (SYN) |
| Final role claim | financing | commercial supply | technology supply |
| Occurrence status | planned | occurred | occurred |
| Identification status | key_based | merged | verified |
| Earlier identification claim | none | key_based | key_based |
| Resolution | resolved to Vendor Beta (SYN) | resolved to Vendor Beta (SYN) | resolved to Vendor K (SYN) |
| Earlier resolution claim | none | none | unresolvable_candidate_set, with candidates Vendor K (SYN) and Utility K (SYN) |

Groups A and B also receive what the base composition lacks: occurrence status *occurred*, identification status
*key_based*, and for each actor reference a final resolution claim that gives its present status (and organisation, for
B), with the provenance below. The status of each group and each reference is the status of its final claim.

Provenance of the claims (every activity has one qualified association per plan, naming its agent and that plan):

| Claims | Activity label | Agent | Plans |
|---|---|---|---|
| role claims | Role coding v3 (SYN) (exists) | Coding model M3 (SYN) | Codebook v3.0 (SYN), Prompt specification v3 (SYN) |
| occurrence claims | Occurrence coding (SYN) | Coding model M3 (SYN) | Occurrence coding protocol (SYN), which is a prompt specification |
| key_based identification claims | Clustering (SYN) | Aggregation pipeline (SYN), software that is not a language model | the month-granularity clustering rule, labelled Month granularity rule (SYN) |
| merged and verified identification claims | Identification re-check (SYN) | Adjudicator (SYN) (exists) | Identification re-check protocol (SYN) |
| final resolution claims of A, B, C, D | Reference resolution (SYN) | Adjudicator (SYN) | Reference resolution rules (SYN) |
| earlier resolution claim of E | Reference resolution by model (SYN) | Coding model M3 (SYN) | Reference resolution rules (SYN), Prompt specification v3 (SYN) |
| final resolution claim of E | Reference re-judgement (SYN) | Adjudicator (SYN) | Reference resolution rules (SYN) |

A later claim that corrects an earlier one is linked to it (`prov:wasRevisionOf`). The earlier claim remains in the
graph and is not final.

IRIs for what is the same thing in both encodings follow the base files: `syn:record-C1`, `syn:article-C1`,
`syn:participation-C-export`, `syn:participation-C-host`, `syn:reference-C-export`, and so on.

## 3. Questions and expected answers

Every answer is compared with the rows below and between the encodings. The value `group` is the letter of the group.
Status values are the notations shown.

**Q4.** For every report group: its occurrence status, its identification status, and whether it is taken as reporting
an engagement.

| group | occurrence | identification | reportsEngagement |
|---|---|---|---|
| A | occurred | key_based | yes |
| B | occurred | key_based | yes |
| C | planned | key_based | no |
| D | occurred | merged | no |
| E | occurred | verified | yes |

**Q5.** Which organisations are asserted to have taken part in which groups, which role facets did they take there
(export and host side are not facets), and on what does the identification of the group rest?

| organisation | role | group | identification |
|---|---|---|---|
| Vendor Beta (SYN) | financing | B | key_based |
| Vendor Beta (SYN) | technology_supply | B | key_based |
| Vendor K (SYN) | technology_supply | E | verified |

**Q6.** For group E and its export-side reference: for each of the three judgements, the final status, the activity,
the agent and the plans of the final claim, and the status given by the claim it revised, if any.

| kind | status | activity | agent | plans | revisedStatus |
|---|---|---|---|---|---|
| identification | verified | Identification re-check (SYN) | Adjudicator (SYN) | Identification re-check protocol (SYN) | key_based |
| occurrence | occurred | Occurrence coding (SYN) | Coding model M3 (SYN) | Occurrence coding protocol (SYN) | |
| resolution | resolved | Reference re-judgement (SYN) | Adjudicator (SYN) | Reference resolution rules (SYN) | unresolvable_candidate_set |

## 4. Constraints

- **c5 (occurrence).** Every report group has exactly one occurrence status and exactly one final claim about it, and
  the claim gives that status. A claim names the one activity that made it.
- **c6 (identification).** The same for the identification status.
- **c7 (resolution).** Every actor reference has exactly one final resolution claim, which gives its status and, when
  the reference is resolved, its organisation.
- **c8 (what is asserted).** An organisation is asserted to have taken part in a group, or to have realized a role
  there, only if the group occurred and is not merged. The coded values of any other group, its reference and its
  claims, stay in the graph as coded values and claims.

Each constraint is implemented in SHACL (SHACL-SPARQL allowed), with vocabulary mixed into the data graph and
`inference="none"`, as in the base comparison.

## 5. Broken variants

Each is a SPARQL update applied in memory to the extended graph, one per encoding, written by whoever wrote that
encoding. Each must be caught by the shapes of its own constraint.

| Variant | Change |
|---|---|
| c5a | group B keeps its occurrence status but loses its final occurrence claim |
| c5b | group C's status is changed to occurred while its final claim still says planned |
| c6a | group E's identification status is changed to key_based while its final claim still says verified |
| c7a | the export-side reference of group E loses its final resolution claim |
| c7b | the export-side reference of group B is resolved to Vendor K (SYN) while its final claim still says Vendor Beta (SYN) |
| c8a | Vendor Beta (SYN) is asserted to have taken part in the planned group C |
| c8b | Vendor Beta (SYN) is asserted to have taken part in the merged group D |

## 6. What is counted

The same measures as the base comparison: triples per section; schema terms, published and ad hoc; codes; shapes per
constraint with their lines and triples; triple patterns per query; whether the answers agree; which variants are
caught. The new material is divided into sections so that like is counted with like:

| Section | Content |
|---|---|
| G | groups C, D and E: event or cluster, records, articles, participations, labels, role claims |
| O | occurrence status of groups C, D and E, with claims |
| I | identification status of groups C, D and E, with claims, activities and plans |
| R | resolution of the references of groups C, D and E, with claims, activities and plans |
| W | what is asserted about the real world for groups C, D and E |
| B0 | in the composition only: what the base NuProc encoding already holds for groups A and B and their shared activities (statuses, claims, occurrence coding, clustering, reference resolution); not compared |

The ad hoc terms are in a section X3, and the builder's new codes in a section X4.

## 7. Shapes counted on the NuProc side

Shipped in `ontology/nuproc-shapes.ttl`, fixed here from their definitions before any run:

| Constraint | Shapes |
|---|---|
| c5 | `EngagementClusterShape`, `OccurrenceClaimShape`, `EngagementClusterProfileShape` |
| c6 | `EngagementClusterShape`, `IdentificationClaimShape`, `EngagementClusterProfileShape` |
| c7 | `ActorReferenceShape`, `ResolutionClaimShape`, `ActorReferenceProfileShape` |
| c8 | `EngagementClusterShape`, `ReportsEngagementShape`, `EngagementRoleShape`, `EngagementShape` |
