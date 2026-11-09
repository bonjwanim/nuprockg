# Licences and scope of this repository

This repository redistributes **none** of the records supplied by the news provider. The licences below apply only to
what the authors hold the rights to: the ontology, its documentation, the queries and the synthetic examples.

## 1. What is public, what is available on request, what is not distributed

This table is the authoritative statement of the scope of the release. The sections *What is in this release* and
*Access* of `README.md` follow it; if they differ, this table prevails.

| Item | Path | Status | Licence |
|---|---|---|---|
| The four ontology modules and their checksums | `ontology/nuproc-{core,codebook,alignments,shapes}.ttl`, `ontology/CHECKSUMS.txt` | **public** | CC BY 4.0, declared with `dcterms:license` in each module |
| Ontology documentation | `docs/ontology/index.html` | **public** | CC BY 4.0 |
| Queries of this version | `queries/v0.9/**/*.rq`, `queries/examples/*.rq` | **public** | CC BY 4.0 |
| Synthetic demonstration graph | `kg/public/nuproc-demo.ttl`; no real event, article or actor | **public** | CC BY 4.0 |
| Synthetic test materials | `tests/**`: the test graphs of the shapes with their expected results and runner, and the comparison with a composition of existing vocabularies | **public** | CC BY 4.0 |
| Top-level documents | `README.md`, `CHANGELOG.md`, `CITATION.cff`, this file, `.gitattributes` | **public** | CC BY 4.0 |
| Licence text | `LICENSE`: the Creative Commons CC BY 4.0 legal code | **public** | dedicated to the public domain by Creative Commons (CC0) |
| Coding prompts, coding, validation and evaluation protocols, codebooks | not in this repository | on request | CC BY 4.0 |
| Analysis code: build, validation, evaluation and checks, with its environment files | not in this repository | on request | MIT |
| Evaluation records, run logs, registry tables and case-level aggregate tables | not in this repository | on request | CC BY 4.0 |
| Design records and the files of earlier versions | not in this repository; see *Design records* and *Earlier versions* in `README.md` | on request | CC BY 4.0 |
| Files that contain personal names | not in this repository | not distributed | none |
| Manuscript drafts | not in this repository | not distributed, owing to the journal's policy on submitted versions | none |
| Record-level knowledge graph | not in this repository | not distributed, owing to the provider's terms | none |
| Source news records | not in this repository | not distributed, owing to the provider's terms | none |

Material marked *on request* is available from the corresponding author on reasonable request, because it is part of
ongoing doctoral research. This applies only to the authors' own work: record-level data and news articles cannot be
provided on request.

### Anything not listed

- Executable code: MIT.
- Any other work of the authors (documents, vocabularies, queries, aggregate or synthetic data): CC BY 4.0.
- Record-level material derived from the provider: no licence is granted, and it is not distributed.

## 2. Why the records are not distributed

The terms of the provider (NewsAPI.ai / Event Registry) restrict the redistribution of records and of datasets, metadata
and derivatives. The news were collected under a paid subscription, to which the provider's licence of use applies.
All record-level material is therefore withheld, and only the authors' own work is published or provided on request.

## 3. Citation

See `CITATION.cff`. CC BY 4.0 requires attribution: please name the authors and the version when reusing the ontology.

## 4. Identifiers

| Item | State |
|---|---|
| Namespace `https://w3id.org/nuproc/` | registered at w3id.org |
| Archive DOI | none; the release is fixed by the tag `tbox-v0.9.0` and `ontology/CHECKSUMS.txt` |
| ORCID | not supplied, so the field is left empty |
