#!/usr/bin/env python3
"""Check that every published term the composition of this folder uses is declared in its vocabulary.

    python -P check_terms.py --dir DIR      # vocabulary files already downloaded into DIR
    python -P check_terms.py --fetch DIR    # download them into DIR first (urllib, generic User-Agent, no contact data)

The vocabularies are those of vocabularies.csv in the parent folder and of vocabularies.csv here (schema.org and ADMS).
The files are third-party documents and are not redistributed; the two lists give the address and the sha256 of each
copy that was checked. A copy whose sha256 differs is still checked, and the difference is reported.
Writes results/term_check.csv (sorted, no time stamp).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
_spec = importlib.util.spec_from_file_location("composition_base_terms", PARENT / "check_terms.py")
ct = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ct)

FILES = ("composition_status.ttl", "composition_status_ext.ttl", "composition_status_shapes.ttl")
QUERIES = ("composition_q4.rq", "composition_q5.rq", "composition_q6.rq")


def used_terms() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}

    def add(iri: str, where: str) -> None:
        if not iri.startswith(ct.SKIP):
            out.setdefault(iri, set()).add(where)

    for name in FILES:
        g = Graph()
        g.parse(HERE / name, format="turtle")
        for t in g:
            for x in t:
                if isinstance(x, URIRef):
                    add(str(x), name)
                elif isinstance(x, Literal) and "SELECT" in str(x):
                    for iri in re.findall(r"<([^>]+)>", str(x)):
                        add(iri, name)
    for name in QUERIES:
        q = prepareQuery((HERE / name).read_text(encoding="utf-8"))
        seen = set()

        def walk(n):
            if id(n) in seen:
                return
            seen.add(id(n))
            if isinstance(n, URIRef):
                add(str(n), name)
            elif isinstance(n, dict):
                for v in n.values():
                    walk(v)
            elif isinstance(n, (list, tuple, set)):
                for v in n:
                    walk(v)
        walk(q.algebra)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dir", type=Path)
    grp.add_argument("--fetch", type=Path)
    a = ap.parse_args()
    base = a.dir or a.fetch
    rows = list(csv.DictReader((PARENT / "vocabularies.csv").open(encoding="utf-8")))
    rows += list(csv.DictReader((HERE / "vocabularies.csv").open(encoding="utf-8")))
    if a.fetch:
        for r in rows:
            ct.fetch(r, base)
    graphs: dict[str, Graph] = {}
    status: dict[str, str] = {}
    for r in rows:
        data = (base / r["file"]).read_bytes()
        ok = ct.sha256(data) == r["sha256"]
        status[r["file"]] = "sha256 as recorded" if ok else f"sha256 DIFFERS ({ct.sha256(data)[:16]})"
        graphs.setdefault(r["namespace"], Graph()).parse(data=data, format=r["format"], publicID=r["url"])
    vocab_of: dict[str, str] = {}
    files_of: dict[str, list[str]] = {}
    for r in rows:
        vocab_of.setdefault(r["namespace"], r["vocabulary"])
        files_of.setdefault(r["namespace"], []).append(r["file"])
    out = []
    for iri, where in sorted(used_terms().items()):
        ns = max((n for n in graphs if iri.startswith(n)), key=len, default=None)
        if ns is None:
            out.append([iri, "(no vocabulary listed)", "NOT CHECKED", "", " ".join(sorted(where)), ""])
            continue
        g = graphs[ns]
        out.append([iri, vocab_of[ns], "yes" if (URIRef(iri), None, None) in g else "NO", ct.describe(g, URIRef(iri)),
                    " ".join(sorted(where)), "; ".join(status[f] for f in files_of[ns])])
    (HERE / "results").mkdir(exist_ok=True)
    ct.write_csv(HERE / "results" / "term_check.csv",
                 ["term", "vocabulary", "declared", "definition_domain_range", "used_in", "vocabulary_file"], out)
    bad = [r for r in out if r[2] != "yes"]
    print(f"published terms used: {len(out)}; declared in their vocabulary: {sum(1 for r in out if r[2] == 'yes')}; "
          f"not declared or not checked: {len(bad)}")
    for r in bad:
        print("  ", r[0], r[1], r[2])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
