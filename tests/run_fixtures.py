#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Wonbae Park
"""Validate the NuProc SHACL test graphs and compare every result with tests/fixtures/EXPECTED.csv.

Needs Python 3.10 or later, rdflib and pySHACL, and nothing else from this repository than the four modules in
ontology/ and the files in tests/fixtures/.

    python tests/run_fixtures.py             # prints one line per test graph and a summary; exit status 0 if all pass

Each test graph is merged with the three vocabulary modules (nuproc-core.ttl, nuproc-codebook.ttl and
nuproc-alignments.ttl, so that class hierarchies and the SKOS schemes of the codes are in the data graph) and validated
with ontology/nuproc-shapes.ttl by pySHACL (advanced=True for the SPARQL constraints, inference="none"), twice:

  all shapes       a positive graph conforms; a negative graph is reported by exactly the named node shapes in the
                   column all_shapes, and every result has the severity in the column severity
  pattern only     the shapes whose nuproc:shapeLayer is not "pattern" are deactivated; a positive graph conforms, and
                   a negative graph is reported by the shape in the column pattern_shapes_only alone (sh:Violation),
                   or conforms where that column says so, because the rule it breaks is a rule of the NuProc profile

A validation result is attributed to the named node shape from which its source shape is reached (through
sh:property, sh:node, sh:not, sh:qualifiedValueShape, sh:sparql, sh:or, sh:and and sh:xone).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import RDF

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
SH = "http://www.w3.org/ns/shacl#"
DEACTIVATE_NON_PATTERN = (
    "PREFIX sh: <http://www.w3.org/ns/shacl#> PREFIX nuproc: <https://w3id.org/nuproc/ns#> "
    "INSERT { ?s sh:deactivated true } WHERE { ?s a sh:NodeShape . FILTER NOT EXISTS { ?s nuproc:shapeLayer \"pattern\" } }"
)


def load(*names: str) -> Graph:
    g = Graph()
    for n in names:
        g.parse(str(ROOT / "ontology" / n), format="turtle")
    return g


def owners(shapes: Graph) -> dict:
    """Each blank node shape → the named node shape it belongs to."""
    links = [URIRef(SH + x) for x in ("property", "node", "not", "qualifiedValueShape", "sparql")]
    lists = [URIRef(SH + x) for x in ("or", "and", "xone")]
    owner: dict = {}
    for named in sorted({s for s in shapes.subjects(RDF.type, URIRef(SH + "NodeShape")) if isinstance(s, URIRef)},
                        key=str):
        stack, seen = [named], {named}
        while stack:
            cur = stack.pop()
            found = [o for p in links for o in shapes.objects(cur, p)]
            found += [i for p in lists for lst in shapes.objects(cur, p) for i in shapes.items(lst)]
            for o in found:
                if isinstance(o, BNode) and o not in seen:
                    seen.add(o)
                    owner.setdefault(o, named)
                    stack.append(o)
        owner.setdefault(named, named)
    return owner


def run(path: Path, shapes: Graph, vocab: Graph, owner: dict) -> tuple[bool, set, set]:
    data = Graph()
    data.parse(str(path), format="turtle")
    for t in vocab:
        data.add(t)
    conforms, report, _ = validate(data, shacl_graph=shapes, advanced=True, inference="none")
    nested = set(report.objects(None, URIRef(SH + "detail")))
    names, sevs = set(), set()
    for r in report.subjects(RDF.type, URIRef(SH + "ValidationResult")):
        if r in nested:
            continue
        for s in report.objects(r, URIRef(SH + "sourceShape")):
            n = owner.get(s, s)
            names.add(str(n).rsplit("#", 1)[-1] if isinstance(n, URIRef) else "(blank)")
        for s in report.objects(r, URIRef(SH + "resultSeverity")):
            sevs.add(str(s).rsplit("#", 1)[-1])
    return conforms, names, sevs


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    vocab = load("nuproc-core.ttl", "nuproc-codebook.ttl", "nuproc-alignments.ttl")
    full = load("nuproc-shapes.ttl")
    pattern = load("nuproc-shapes.ttl")
    pattern.update(DEACTIVATE_NON_PATTERN)
    own_full, own_pattern = owners(full), owners(pattern)
    with (FIXTURES / "EXPECTED.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    files = sorted(p.relative_to(FIXTURES).as_posix() for p in FIXTURES.glob("*/*.ttl"))
    failed = [f"{x}: no expected result" for x in sorted(set(files) - {r["file"] for r in rows})]
    failed += [f"{r['file']}: listed but missing" for r in rows if r["file"] not in files]
    n_ok = 0
    for r in rows:
        path = FIXTURES / r["file"]
        if not path.is_file():
            continue
        c, names, sevs = run(path, full, vocab, own_full)
        if r["all_shapes"] == "conforms":
            ok_full = c
        else:
            ok_full = (not c) and names == set(r["all_shapes"].split()) and sevs == {r["severity"]}
        cp, names_p, sevs_p = run(path, pattern, vocab, own_pattern)
        if r["pattern_shapes_only"] == "conforms":
            ok_pattern = cp
        else:
            ok_pattern = (not cp) and names_p == {r["pattern_shapes_only"]} and sevs_p == {"Violation"}
        mark = "ok  " if ok_full and ok_pattern else "FAIL"
        print(f"{mark} {r['file']:70s} all shapes: {'conforms' if c else ' '.join(sorted(names))}"
              f" | pattern only: {'conforms' if cp else ' '.join(sorted(names_p))}")
        if ok_full and ok_pattern:
            n_ok += 1
        else:
            failed.append(r["file"])
    n_pos = sum(1 for r in rows if r["file"].startswith("positive/"))
    print(f"\n{len(rows)} test graphs ({n_pos} positive, {len(rows) - n_pos} negative); "
          f"{n_ok} as expected, {len(rows) - n_ok} not")
    for x in failed:
        print("  not as expected: " + x)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
