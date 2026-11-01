# Test materials for NuProc 0.9.0

Everything in this folder is synthetic: no real organization, article or event appears in it. It runs with Python
3.10 or later, rdflib and pySHACL, and reads nothing from the repository but the four modules in `ontology/`.
They were checked with Python 3.14.3, rdflib 7.6.0 and pySHACL 0.40.1.

## SHACL test graphs (`fixtures/`)

`fixtures/positive/` holds 15 graphs that must conform to `ontology/nuproc-shapes.ttl`; `fixtures/negative/` holds
97 graphs, each of which breaks one rule. `fixtures/EXPECTED.csv` gives, for every graph, the named node shapes that
must report it with all shapes active (`all_shapes`, with the `severity` of every result), and the result with only
the shapes of the pattern layer active (`pattern_shapes_only`). A negative graph that breaks a rule of the NuProc
profile conforms when only the pattern-layer shapes are active; a few of the negative graphs that break a pattern
rule are also reported by a profile shape when all shapes are active, and `all_shapes` lists both. The domain
regularities of the profile report warnings (`severity` Warning); every other rule reports violations.

```bash
python tests/run_fixtures.py    # one line per test graph, then a summary; exit status 0 when all 112 are as expected
```

Each graph is merged with `nuproc-core.ttl`, `nuproc-codebook.ttl` and `nuproc-alignments.ttl` before validation, so
that the class hierarchy and the concept schemes of the codes are in the data graph, and is validated by pySHACL with
`advanced=True` (the SPARQL constraints) and `inference="none"`. A result is attributed to the named node shape from
which its source shape is reached. The run takes about two minutes.

The individuals of the test graphs have IRIs under `https://w3id.org/nuproc/fixture/`; w3id redirects that path to this
file.

## The same case in a composition of existing vocabularies (`composition_example/`)

One synthetic case expressed twice: in a composition of existing vocabularies with no NuProc term (SEM, GAF, PROV-O,
W3C ORG and SKOS, plus three ad hoc properties), and in NuProc 0.9.0. The same three questions, four constraints and
broken variants are run on both. `composition_example/README.md` describes the case, the choices and the results.

```bash
python tests/composition_example/run.py    # rebuilds composition_example/results/ (sorted, no time stamp)
```

## Licence

CC BY 4.0, as the rest of the repository (`LICENSE`), including the Python scripts in this folder.
