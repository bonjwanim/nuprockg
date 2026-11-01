#!/usr/bin/env python3
"""Check that every published term the two encodings use is declared in its vocabulary, and record the facts the
README states about the terms that were considered and not used. NuProc's own terms and codes are checked by run.py
against the NuProc modules; the BFO and RO relations, which NuProc declares by IRI, are not checked here.

    python -P check_terms.py --dir DIR      # vocabulary files already downloaded into DIR (layout: vocabularies.csv)
    python -P check_terms.py --fetch DIR    # download them into DIR first (urllib, generic User-Agent, no contact data)

The vocabulary files are third-party documents and are not redistributed here; vocabularies.csv gives the address and
the sha256 of each copy that was checked. A copy whose sha256 differs is still checked, and the difference is
reported. Writes results/term_check.csv and results/term_check_considered.csv (sorted, no time stamp).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
import urllib.request
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS
from rdflib.plugins.sparql import prepareQuery

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
UA = "Mozilla/5.0 (compatible; vocabulary-check/1.0)"
SKIP = ("http://www.w3.org/ns/shacl#", "http://www.w3.org/2001/XMLSchema#", "https://example.org/",
        "https://w3id.org/nuproc/", "http://purl.obolibrary.org/obo/")

# Terms the README discusses as considered and not used, with the facts it relies on.
CONSIDERED = [
    "http://data.europa.eu/a4g/ontology#AgentInRole",
    "http://data.europa.eu/a4g/ontology#playedBy",
    "http://data.europa.eu/a4g/ontology#contextualisedBy",
    "http://data.europa.eu/a4g/ontology#OfferingParty",
    "http://data.europa.eu/a4g/ontology#AcquiringParty",
    "http://semanticweb.cs.vu.nl/2009/11/sem/View",
    "http://semanticweb.cs.vu.nl/2009/11/sem/accordingTo",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt",
    "http://www.w3.org/2002/07/owl#oneOf",
    "http://groundedannotationframework.org/gaf#denotedBy",
    "http://www.w3.org/ns/org#Role",
    "http://wikiba.se/ontology#rank",
]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(row: dict, base: Path) -> None:
    headers = {"User-Agent": UA}
    if row["accept"]:
        headers["Accept"] = row["accept"]
    with urllib.request.urlopen(urllib.request.Request(row["url"], headers=headers), timeout=120) as r:
        body = r.read()
    dest = base / row["file"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)


def used_terms() -> dict[str, set[str]]:
    """Every IRI the files of both encodings use (outside SKIP), with the files that use it."""
    out: dict[str, set[str]] = {}

    def add(iri: str, where: str) -> None:
        if iri.startswith(SKIP):
            return
        out.setdefault(iri, set()).add(where)

    for name in ("composition.ttl", "composition_ext.ttl", "composition_shapes.ttl", "nuproc.ttl"):
        g = Graph()
        g.parse(HERE / name, format="turtle")
        for t in g:
            for x in t:
                if isinstance(x, URIRef):
                    add(str(x), name)
                elif isinstance(x, Literal) and "SELECT" in str(x):
                    for iri in re.findall(r"<([^>]+)>", str(x)):
                        add(iri, name)
    for p in sorted(HERE.glob("*_q[0-9].rq")):
        text = p.read_text(encoding="utf-8")
        q = prepareQuery(text)
        seen = set()

        def walk(n):
            if id(n) in seen:
                return
            seen.add(id(n))
            if isinstance(n, URIRef):
                add(str(n), p.name)
            elif isinstance(n, dict):
                for v in n.values():
                    walk(v)
            elif isinstance(n, (list, tuple, set)):
                for v in n:
                    walk(v)
        walk(q.algebra)
    return out


def describe(g: Graph, s: URIRef) -> str:
    parts = []
    for p in (SKOS.definition, RDFS.comment):
        for o in sorted(g.objects(s, p)):
            parts.append(re.sub(r"\s+", " ", str(o))[:220])
            break
        if parts:
            break
    for p, label in ((RDFS.domain, "domain"), (RDFS.range, "range")):
        for o in sorted(g.objects(s, p), key=str):
            parts.append(f"{label} {('<' + str(o) + '>') if isinstance(o, URIRef) else '(class expression)'}")
    return " | ".join(parts)


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dir", type=Path)
    grp.add_argument("--fetch", type=Path)
    a = ap.parse_args()
    base = a.dir or a.fetch
    rows = list(csv.DictReader((HERE / "vocabularies.csv").open(encoding="utf-8")))
    if a.fetch:
        for r in rows:
            fetch(r, base)

    graphs: dict[str, Graph] = {}
    status: dict[str, str] = {}
    for r in rows:
        path = base / r["file"]
        data = path.read_bytes()
        ok = sha256(data) == r["sha256"]
        status[r["file"]] = "sha256 as recorded" if ok else f"sha256 DIFFERS ({sha256(data)[:16]})"
        g = graphs.setdefault(r["namespace"], Graph())
        g.parse(data=data, format=r["format"], publicID=r["url"])
    files_of = {}
    for r in rows:
        files_of.setdefault(r["namespace"], []).append(r["file"])
    vocab_of: dict[str, str] = {}
    for r in rows:                                   # the first row of a namespace names it
        vocab_of.setdefault(r["namespace"], r["vocabulary"])

    out = []
    for iri, where in sorted(used_terms().items()):
        ns = max((n for n in graphs if iri.startswith(n)), key=len, default=None)
        if ns is None:
            out.append([iri, "(no vocabulary listed)", "NOT CHECKED", "", " ".join(sorted(where)), ""])
            continue
        g = graphs[ns]
        declared = (URIRef(iri), None, None) in g
        out.append([iri, vocab_of[ns], "yes" if declared else "NO", describe(g, URIRef(iri)),
                    " ".join(sorted(where)), "; ".join(status[f] for f in files_of[ns])])
    RES.mkdir(exist_ok=True)
    write_csv(RES / "term_check.csv",
              ["term", "vocabulary", "declared", "definition_domain_range", "used_in", "vocabulary_file"], out)

    cons = []
    for iri in CONSIDERED:
        ns = max((n for n in graphs if iri.startswith(n)), key=len)
        g = graphs[ns]
        s = URIRef(iri)
        facts = describe(g, s)
        restr = []
        for b in g.subjects(OWL.onProperty, s):
            for p, label in ((OWL.cardinality, "cardinality"), (OWL.qualifiedCardinality, "qualified cardinality"),
                             (OWL.maxCardinality, "max cardinality"), (OWL.minCardinality, "min cardinality")):
                for v in g.objects(b, p):
                    holders = sorted(str(x).rsplit("#", 1)[-1] for x in g.subjects(RDFS.subClassOf, b))
                    restr.append(f"{label} {v} on {', '.join(holders) or '(anonymous)'}")
        subs = sorted(str(x).rsplit("#", 1)[-1] for x in g.subjects(RDFS.subClassOf, s) if isinstance(x, URIRef))
        cons.append([iri, vocab_of[ns], "yes" if (s, None, None) in g else "NO", facts, "; ".join(sorted(restr)),
                     " ".join(subs)])
    write_csv(RES / "term_check_considered.csv",
              ["term", "vocabulary", "declared", "definition_domain_range", "restrictions", "named_subclasses"], cons)

    bad = [r for r in out if r[2] != "yes"]
    print(f"published terms used by the two encodings: {len(out)}; declared in their vocabulary: "
          f"{sum(1 for r in out if r[2] == 'yes')}; not declared or not checked: {len(bad)}")
    for r in bad:
        print("  ", r[0], r[1], r[2])
    for f, s in sorted(status.items()):
        print(f"  {f}: {s}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
