#!/usr/bin/env python3
"""Rebuild every result in results/ from the .ttl, .rq and .ru files of this folder.

    python run.py                   # the NuProc modules are read from the ontology/ folder of the repository
                                    # validates against the ontology/ files of this checkout

What it does (all output is sorted and carries no time stamp, so a re-run gives identical files):

  1. representation  counts the triples of every section of composition.ttl, nuproc.ttl and composition_ext.ttl
                     and lists the schema terms each section uses, by vocabulary          -> representation.csv,
                                                                                            terms_used.csv
  2. validation      validates each encoding with its shapes (the composition with composition_shapes.ttl, NuProc
                     with the shipped ontology/nuproc-shapes.ttl), then each broken variant in broken/
                                                                                         -> validation.csv,
                                                                                            validation_details.csv
  3. shape sizes     lines and triples of every shape that implements c1-c4, written by the builder or shipped
                                                                                         -> shapes_size.csv
  4. queries         runs q1-q3 on both encodings, saves the answers, compares them and counts their patterns
                                                                                         -> q*_*.csv, query_metrics.csv
  5. summary         the numbers the README quotes                                       -> summary.txt

Validation runs pySHACL with advanced=True (SHACL-SPARQL) and inference="none". The vocabulary of each encoding is
merged into its data graph before validation (NuProc: core + codebook + alignments; composition: composition_ext.ttl),
as scripts/validate_kg.py does. pySHACL's ont_graph argument is not used: in pySHACL 0.40.1 it copies only RDFS and
OWL axioms into the data graph, not the codebook's SKOS concepts, so every check that reads a code's scheme or role
class fails (17 violations on nuproc.ttl); and its full-mixin switch (PYSHACL_USE_FULL_MIXIN) fails with rdflib 7.6.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.paths import Path as RDFPath
from rdflib.term import Variable

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "ontology" / "nuproc-core.ttl").is_file())   # the repository root
RES = HERE / "results"
BROKEN = HERE / "broken"

# The NuProc modules are read from the ontology/ folder of the repository.
NUPROC_MODULES = ["nuproc-core.ttl", "nuproc-codebook.ttl", "nuproc-alignments.ttl"]
NUPROC_SHAPES = "nuproc-shapes.ttl"

SH = "http://www.w3.org/ns/shacl#"
SH_RESULT = URIRef(SH + "ValidationResult")

PREFIXES = {
    "sem": "http://semanticweb.cs.vu.nl/2009/11/sem/",
    "gaf": "http://groundedannotationframework.org/gaf#",
    "prov": "http://www.w3.org/ns/prov#",
    "org": "http://www.w3.org/ns/org#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "time": "http://www.w3.org/2006/time#",
    "obo": "http://purl.obolibrary.org/obo/",
    "nuproc": "https://w3id.org/nuproc/ns#",
    "channel": "https://w3id.org/nuproc/channel/",
    "etype": "https://w3id.org/nuproc/eventtype/",
    "crole": "https://w3id.org/nuproc/counterpartyrole/",
    "erole": "https://w3id.org/nuproc/engagementrole/",
    "srole": "https://w3id.org/nuproc/siderole/",
    "rstat": "https://w3id.org/nuproc/resolutionstatus/",
    "ex": "https://example.org/ext#",
    "exrole": "https://example.org/ext/role/",
    "exside": "https://example.org/ext/side/",
    "excp": "https://example.org/ext/counterparty/",
    "exstat": "https://example.org/ext/status/",
    "explan": "https://example.org/ext/plantype/",
    "extype": "https://example.org/ext/eventtype/",
    "syn": "https://example.org/syn/",
    "cs": "https://example.org/composition-shapes#",
    "sh": SH,
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}
# Which vocabulary a schema term comes from. Codes (SKOS concepts) are counted apart from schema terms.
VOCAB = {
    "sem": "SEM", "gaf": "GAF", "prov": "PROV-O", "org": "W3C ORG", "skos": "SKOS", "dcterms": "DCTERMS",
    "rdf": "RDF", "rdfs": "RDFS", "owl": "OWL", "time": "OWL-Time", "obo": "BFO/RO", "nuproc": "NuProc",
    "ex": "ad hoc",
}
CODE_PREFIXES = {"channel", "etype", "crole", "erole", "srole", "rstat",
                 "exrole", "exside", "excp", "exstat", "explan", "extype"}

# The shapes that implement each constraint. NuProc ships them; the builder of the composition writes them.
CONSTRAINT_SHAPES = {
    "composition": {
        "c1": ["cs:C1_CandidateSetReferenceShape"],
        "c2": ["cs:C2_ClaimShape", "cs:C2_FinalClaimShape"],
        "c3": ["cs:C3_CodingActivityShape", "cs:C3_AssociationShape"],
        "c4": ["cs:C4_RoleInEngagementShape"],
    },
    "nuproc": {
        # a reference must also agree with its final resolution claim (c1b changes the status, so the two disagree)
        "c1": ["nuproc:AmbiguousReferenceCandidateShape", "nuproc:ReferenceKindStatusShape",
               "nuproc:ActorReferenceShape", "nuproc:ResolutionStatusConceptShape", "nuproc:ResolutionClaimShape"],
        "c2": ["nuproc:CodedParticipationRoleClaimShape", "nuproc:RoleClaimShape"],
        # the rule that a model's coding activity follows a prompt specification is a profile shape
        "c3": ["nuproc:CodingActivityShape", "nuproc:AssociationShape", "nuproc:CodingActivityProfileShape"],
        "c4": ["nuproc:EngagementShape", "nuproc:EngagementRoleShape"],
    },
}
CONSTRAINTS = {
    "c1": "a candidate-set reference names at least two candidates and is not marked resolved",
    "c2": "every role value on a participation has exactly one final claim that agrees with it",
    "c3": "a coding activity has a qualified association per plan; a model activity has a prompt-specification plan",
    "c4": "a role's bearer participates in the engagement that realizes it",
}
PHENOMENON_OF_CONSTRAINT = {"c1": "candidate set", "c2": "divergent claims", "c3": "divergent claims",
                            "c4": "multiple roles"}
SECTION_PHENOMENON = {"P1": "candidate set", "P2": "divergent claims", "P3": "multiple roles"}


# ----------------------------------------------------------------------------------------------------------------
# inputs

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_nuproc(name: str) -> tuple[str, str]:
    """Text of an ontology module, and where it came from."""
    data = (ROOT / "ontology" / name).read_bytes()
    return data.decode("utf-8"), f"ontology/{name}"


def parse(text: str) -> Graph:
    g = Graph()
    g.parse(data=text, format="turtle")
    return g


def merged(*graphs: Graph) -> Graph:
    g = Graph()
    for x in graphs:
        for t in x:
            g.add(t)
    return g


def short(term) -> str:
    if isinstance(term, URIRef):
        s = str(term)
        best = None
        for p, ns in PREFIXES.items():
            if s.startswith(ns) and (best is None or len(ns) > len(PREFIXES[best])):
                best = p
        if best is not None:
            return f"{best}:{s[len(PREFIXES[best]):]}"
        return f"<{s}>"
    if isinstance(term, BNode):
        return "_:b"
    if isinstance(term, Literal):
        return str(term)
    return str(term)


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(["" if v is None else v for v in r])
    path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")


# ----------------------------------------------------------------------------------------------------------------
# 1. representation

SECTION_RE = re.compile(r"^# == (\w+) (.*?) ==\s*$")


def sections(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """(prefix header, [(section id, title, body)])."""
    lines = text.splitlines(keepends=True)
    header, out, cur = [], [], None
    for ln in lines:
        m = SECTION_RE.match(ln)
        if m:
            cur = [m.group(1), m.group(2), []]
            out.append(cur)
        elif cur is None:
            header.append(ln)
        else:
            cur[2].append(ln)
    return "".join(header), [(a, b, "".join(c)) for a, b, c in out]


CLASSES_SEEN: set[str] = set()


def schema_terms(g: Graph) -> tuple[Counter, Counter]:
    """(schema terms: predicates other than rdf:type and the classes of rdf:type, codes used as objects)."""
    terms, codes = Counter(), Counter()
    for s, p, o in g:
        if p != RDF.type:
            terms[short(p)] += 1
        else:
            terms[short(o)] += 1
            CLASSES_SEEN.add(short(o))
        if isinstance(o, URIRef) and short(o).split(":")[0] in CODE_PREFIXES and p != RDF.type:
            codes[short(o)] += 1
    return terms, codes


def representation(texts: dict[str, str], declared: dict[str, set[str]]) -> tuple[list, list, dict]:
    rep_rows, term_rows, totals = [], [], {}
    for fname, text in texts.items():
        header, secs = sections(text)
        whole = parse(text)
        union, n_sum = Graph(), 0
        used_in = defaultdict(set)
        uses = Counter()
        for sid, title, body in secs:
            g = parse(header + body)
            n_sum += len(g)
            for t in g:
                union.add(t)
            terms, codes = schema_terms(g)
            for t, n in terms.items():
                used_in[t].add(sid)
                uses[t] += n
            published = sorted(t for t in terms if not t.startswith("ex:"))
            adhoc = sorted(t for t in terms if t.startswith("ex:"))
            rep_rows.append([fname, sid, title, len(g), len(published), len(adhoc), " ".join(adhoc),
                             len(codes), " ".join(sorted(codes))])
        if len(union) != len(whole) or n_sum != len(whole):
            raise SystemExit(f"{fname}: sections do not partition the file ({n_sum} / {len(union)} / {len(whole)})")
        totals[fname] = len(whole)
        rep_rows.append([fname, "ALL", "whole file", len(whole), "", "", "", "", ""])
        for t in sorted(uses):
            pfx = t.split(":")[0]
            kind = "class" if t in CLASSES_SEEN else "property"
            if pfx == "nuproc":
                decl = "yes" if t in declared["nuproc"] else "NO"
            elif pfx == "ex":
                decl = "yes" if t in declared["ex"] else "NO"
            elif pfx == "obo":
                decl = "declared by IRI in nuproc-core.ttl" if t in declared["obo"] else "NO"
            else:
                decl = "see term_check.csv"
            term_rows.append([fname, t, kind, VOCAB.get(pfx, pfx), " ".join(sorted(used_in[t])), uses[t], decl])
    return rep_rows, term_rows, totals


# ----------------------------------------------------------------------------------------------------------------
# 2. validation

def owner(shapes: Graph, node) -> str:
    """The named shape a (possibly blank) shape node belongs to."""
    seen = set()
    frontier = [node]
    while frontier:
        n = frontier.pop(0)
        if isinstance(n, URIRef):
            return short(n)
        if n in seen:
            continue
        seen.add(n)
        for s in shapes.subjects(None, n):
            frontier.append(s)
    return "(unnamed)"


def run_validation(data: Graph, shapes: Graph) -> tuple[bool, list[tuple]]:
    from pyshacl import validate
    conforms, rg, _ = validate(data, shacl_graph=shapes, advanced=True, inference="none")
    nested = {o for o in rg.objects(None, URIRef(SH + "detail"))}
    rows = []
    for r in rg.subjects(RDF.type, SH_RESULT):
        if r in nested:
            continue
        sev = short(rg.value(r, URIRef(SH + "resultSeverity"))).split("#")[-1].replace("sh:", "")
        shp = owner(shapes, rg.value(r, URIRef(SH + "sourceShape")))
        focus = short(rg.value(r, URIRef(SH + "focusNode")))
        path = rg.value(r, URIRef(SH + "resultPath"))
        if isinstance(path, BNode) and rg.value(path, URIRef(SH + "inversePath")) is not None:
            path = "^" + short(rg.value(path, URIRef(SH + "inversePath")))
        else:
            path = short(path) if isinstance(path, URIRef) else ("" if path is None else "(complex path)")
        value = rg.value(r, URIRef(SH + "value"))
        value = "" if value is None else short(value)
        msgs = sorted(str(m) for m in rg.objects(r, URIRef(SH + "resultMessage")))
        rows.append((sev, shp, focus, path, value, " / ".join(msgs)))
    return bool(conforms), sorted(set(rows))


def apply_update(g: Graph, ru_text: str) -> Graph:
    h = Graph()
    for t in g:
        h.add(t)
    h.update(ru_text)
    return h


def first_comment(text: str) -> str:
    out = []
    for ln in text.splitlines():
        if ln.startswith("#"):
            out.append(ln.lstrip("# ").strip())
        elif out:
            break
    return " ".join(out)


# ----------------------------------------------------------------------------------------------------------------
# 3. shape sizes

def shape_block(text: str, name: str) -> str:
    """Source text of the statement whose subject is the prefixed name `name` (from its first line to its final '.')."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(re.escape(name) + r"(\s|$)", ln):
            start = i
            break
    if start is None:
        raise SystemExit(f"shape {name} not found")
    depth, in_long, out = 0, False, []
    for ln in lines[start:]:
        out.append(ln)
        i, n, ended = 0, len(ln), False
        while i < n:
            if in_long:
                if ln.startswith('"""', i):
                    in_long = False
                    i += 3
                    continue
                i += 1
                continue
            c = ln[i]
            if ln.startswith('"""', i):
                in_long = True
                i += 3
                continue
            if c == '"':
                j = i + 1
                while j < n and not (ln[j] == '"' and ln[j - 1] != "\\"):
                    j += 1
                i = j + 1
                continue
            if c == "<":
                j = ln.find(">", i)
                i = n if j < 0 else j + 1
                continue
            if c == "#":
                break
            if c in "[(":
                depth += 1
            elif c in "])":
                depth -= 1
            elif c == "." and depth == 0:
                rest = ln[i + 1:].strip()
                if rest == "" or rest.startswith("#"):
                    ended = True
                    break
            i += 1
        if ended and not in_long:
            break
    return "\n".join(out)


def counted_lines(block: str) -> int:
    return sum(1 for ln in block.splitlines() if ln.strip() and not ln.strip().startswith("#"))


def cbd_triples(g: Graph, node: URIRef) -> int:
    seen, frontier, n = set(), [node], 0
    while frontier:
        s = frontier.pop()
        if s in seen:
            continue
        seen.add(s)
        for _, _, o in g.triples((s, None, None)):
            n += 1
            if isinstance(o, BNode):
                frontier.append(o)
    return n


def expand(pname: str) -> URIRef:
    p, local = pname.split(":", 1)
    return URIRef(PREFIXES[p] + local)


# ----------------------------------------------------------------------------------------------------------------
# 4. queries

def walk(node, seen, acc):
    if id(node) in seen:
        return
    seen.add(id(node))
    if isinstance(node, CompValue):
        name = node.name
        if name == "BGP":
            for t in node.get("triples", []):
                acc["triples"].append(tuple(t))
        elif name == "TriplesBlock":             # the graph of an EXISTS stays in parse-tree form after prepareQuery
            for tl in node.get("triples", []):
                for i in range(0, len(tl), 3):
                    acc["triples"].append(tuple(tl[i:i + 3]))
        elif name == "LeftJoin":
            acc["optional"] += 1
        elif name == "Union":
            acc["union"] += 1
        elif name in ("Builtin_EXISTS", "Builtin_NOTEXISTS"):
            acc["exists"] += 1
        elif name.startswith("Aggregate_"):
            acc["aggregates"] += 1
        for v in node.values():
            walk(v, seen, acc)
    elif isinstance(node, (list, tuple)):
        for v in node:
            walk(v, seen, acc)
    elif isinstance(node, dict):
        for v in node.values():
            walk(v, seen, acc)


def query_metrics(text: str) -> dict:
    q = prepareQuery(text)
    acc = {"triples": [], "optional": 0, "union": 0, "exists": 0, "aggregates": 0}
    walk(q.algebra, set(), acc)
    triples = acc["triples"]                     # every pattern as written, including those inside EXISTS
    var_in = Counter()
    terms = set()
    for t in triples:
        for x in set(x for x in t if isinstance(x, Variable)):
            var_in[x] += 1
        p = t[1]
        if isinstance(p, RDFPath):
            for iri in re.findall(r"<([^>]+)>", p.n3()):
                terms.add(short(URIRef(iri)))
        elif isinstance(p, URIRef):
            terms.add(short(p))
            if p == RDF.type and isinstance(t[2], URIRef):
                terms.add(short(t[2]))
    paths = sum(1 for t in triples if isinstance(t[1], RDFPath))
    adhoc = sorted(t for t in terms if t.startswith("ex:"))
    vocabs = sorted({VOCAB.get(t.split(":")[0], t.split(":")[0]) for t in terms if t.split(":")[0] in VOCAB})
    return {
        "triple_patterns": len(triples),
        "property_paths": paths,
        "variables": len(var_in),
        "join_variables": sum(1 for v, n in var_in.items() if n >= 2),
        "optional": acc["optional"],
        "union": acc["union"],
        "exists": acc["exists"],
        "adhoc_terms": " ".join(adhoc),
        "vocabularies": " ".join(vocabs),
    }


def run_query(g: Graph, text: str) -> tuple[list[str], list[list[str]]]:
    res = g.query(text)
    header = [str(v) for v in res.vars]
    rows = []
    for row in res:
        out = []
        for v in row:
            s = "" if v is None else str(v)
            if " | " in s:                       # GROUP_CONCAT order is not defined by SPARQL: sort its items
                s = " | ".join(sorted(s.split(" | ")))
            out.append(s)
        rows.append(out)
    return header, sorted(rows)


# ----------------------------------------------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.parse_args()
    RES.mkdir(exist_ok=True)

    # inputs ------------------------------------------------------------------------------------------------------
    own = ["composition.ttl", "composition_ext.ttl", "composition_shapes.ttl", "nuproc.ttl"]
    own += sorted(p.name for p in HERE.glob("*_q[0-9].rq"))
    texts = {n: (HERE / n).read_text(encoding="utf-8") for n in own}
    broken = {p.name: p.read_text(encoding="utf-8") for p in sorted(BROKEN.glob("*.ru"))}
    nu_texts, nu_src = {}, {}
    for m in NUPROC_MODULES + [NUPROC_SHAPES]:
        nu_texts[m], nu_src[m] = read_nuproc(m)
    input_rows = [[n, "this folder", sha256(texts[n].encode("utf-8"))] for n in own]
    input_rows += [[f"broken/{n}", "this folder", sha256(t.encode("utf-8"))] for n, t in broken.items()]
    input_rows += [[m, nu_src[m], sha256(nu_texts[m].encode("utf-8"))] for m in NUPROC_MODULES + [NUPROC_SHAPES]]
    write_csv(RES / "inputs.csv", ["file", "read_from", "sha256"], input_rows)

    tbox = merged(*(parse(nu_texts[m]) for m in NUPROC_MODULES))
    nu_shapes = parse(nu_texts[NUPROC_SHAPES])
    ext = parse(texts["composition_ext.ttl"])
    co_shapes = parse(texts["composition_shapes.ttl"])
    data = {"composition": parse(texts["composition.ttl"]), "nuproc": parse(texts["nuproc.ttl"])}
    vocab = {"composition": ext, "nuproc": tbox}
    shapes = {"composition": co_shapes, "nuproc": nu_shapes}

    # 1. representation -------------------------------------------------------------------------------------------
    declared = {
        "nuproc": {short(s) for s in tbox.subjects() if isinstance(s, URIRef) and short(s).startswith("nuproc:")},
        "ex": {short(s) for s in ext.subjects() if isinstance(s, URIRef) and short(s).startswith("ex:")},
        "obo": {short(s) for s in tbox.subjects(RDF.type, None) if isinstance(s, URIRef)
                and short(s).startswith("obo:")},
    }
    rep_rows, term_rows, totals = representation(
        {n: texts[n] for n in ("composition.ttl", "nuproc.ttl", "composition_ext.ttl")}, declared)
    write_csv(RES / "representation.csv",
              ["file", "section", "title", "triples", "published_terms", "adhoc_terms", "adhoc_term_list",
               "distinct_codes", "codes"], rep_rows)
    write_csv(RES / "terms_used.csv",
              ["file", "term", "kind", "vocabulary", "sections", "uses", "declared"], term_rows)
    codes_used = {}
    for enc in ("composition", "nuproc"):
        codes_used[enc] = sorted({short(o) for o in data[enc].objects() if isinstance(o, URIRef)
                                  and short(o).split(":")[0] in CODE_PREFIXES})
        missing = [c for c in codes_used[enc] if (expand(c), None, None) not in vocab[enc]]
        if missing:
            raise SystemExit(f"{enc}: codes not declared in its vocabulary: {missing}")

    # 2. validation -----------------------------------------------------------------------------------------------
    val_rows, detail_rows = [], []
    for enc in ("composition", "nuproc"):
        base = merged(data[enc], vocab[enc])
        variants = [("base", "the encoding as written", None)]
        variants += [(n.split("_")[0], first_comment(t), t) for n, t in broken.items() if n.endswith(f"_{enc}.ru")]
        for variant, desc, upd in variants:
            g = base if upd is None else apply_update(base, upd)
            conforms, rows = run_validation(g, shapes[enc])
            n_v = sum(1 for r in rows if r[0] == "Violation")
            n_w = sum(1 for r in rows if r[0] == "Warning")
            fired = sorted({r[1] for r in rows if r[0] == "Violation"})
            if variant == "base":
                target, detected, others = "", "", ""
            else:
                c = variant[:2]
                target = c
                expected = set(CONSTRAINT_SHAPES[enc][c])
                detected = "yes" if expected & set(fired) else "NO"
                others = " ".join(s for s in fired if s not in expected)
            val_rows.append([enc, variant, target, desc, str(conforms).lower(), n_v, n_w, " ".join(fired),
                             detected, others])
            for r in rows:
                detail_rows.append([enc, variant, *r])
    write_csv(RES / "validation.csv",
              ["encoding", "variant", "constraint", "description", "conforms", "violations", "warnings",
               "shapes_fired", "constraint_shape_fired", "other_shapes_fired"], val_rows)
    write_csv(RES / "validation_details.csv",
              ["encoding", "variant", "severity", "shape", "focus_node", "path", "value", "message"], detail_rows)

    # 3. shape sizes ----------------------------------------------------------------------------------------------
    size_rows = []
    shape_text = {"composition": texts["composition_shapes.ttl"], "nuproc": nu_texts[NUPROC_SHAPES]}
    for enc in ("composition", "nuproc"):
        for c, names in CONSTRAINT_SHAPES[enc].items():
            for name in names:
                block = shape_block(shape_text[enc], name)
                size_rows.append([enc, c, name, "builder writes" if enc == "composition" else "shipped with NuProc",
                                  counted_lines(block), cbd_triples(shapes[enc], expand(name))])
    write_csv(RES / "shapes_size.csv", ["encoding", "constraint", "shape", "who", "lines", "triples"], size_rows)
    nu_named = sorted({short(s) for s in nu_shapes.subjects(RDF.type, URIRef(SH + "NodeShape"))
                       if isinstance(s, URIRef)})

    # 4. queries --------------------------------------------------------------------------------------------------
    qm_rows, q_answers = [], {}
    for qn in ("q1", "q2", "q3"):
        for enc in ("composition", "nuproc"):
            qtext = texts[f"{enc}_{qn}.rq"]
            header, rows = run_query(merged(data[enc], vocab[enc]), qtext)
            write_csv(RES / f"{qn}_{enc}.csv", header, rows)
            q_answers[(qn, enc)] = (header, rows)
            m = query_metrics(qtext)
            qm_rows.append([qn, enc, len(rows), m["triple_patterns"], m["property_paths"], m["variables"],
                            m["join_variables"], m["optional"], m["union"], m["exists"], m["adhoc_terms"],
                            m["vocabularies"]])
        same = q_answers[(qn, "composition")] == q_answers[(qn, "nuproc")]
        for r in qm_rows[-2:]:
            r.append("yes" if same else "NO")
    write_csv(RES / "query_metrics.csv",
              ["query", "encoding", "rows", "triple_patterns", "property_paths", "variables", "join_variables",
               "optional", "union", "exists", "adhoc_terms", "vocabularies", "same_answer_as_other_encoding"],
              qm_rows)

    # 5. summary --------------------------------------------------------------------------------------------------
    rep = {(r[0], r[1]): r for r in rep_rows}
    sz = defaultdict(lambda: [0, 0, 0])
    for enc, c, name, who, lines, triples in size_rows:
        sz[(enc, c)][0] += 1
        sz[(enc, c)][1] += lines
        sz[(enc, c)][2] += triples
    ext_header, ext_secs = sections(texts["composition_ext.ttl"])
    ext_lines = {sid: counted_lines(body) for sid, _, body in ext_secs}
    out = []
    # the version is read from the core module, not written by hand
    _v = re.search(r'owl:versionInfo\s+"([^"]+)"', (ROOT / "ontology" / NUPROC_MODULES[0]).read_text(encoding="utf-8"))
    _cur = _v.group(1) if _v else "?"
    out.append(f"NuProc modules read from: the ontology/ folder of the repository (TBox {_cur})")
    out.append("")
    out.append("REPRESENTATION (triples per section; published / ad-hoc schema terms; distinct codes)")
    for sid in ("S0", "S1", "P1", "P2", "P3"):
        a, b = rep[("composition.ttl", sid)], rep[("nuproc.ttl", sid)]
        out.append(f"  {sid} {a[2][:60]:60s} composition {a[3]:3d} triples ({a[4]} published, {a[5]} ad hoc"
                   f"{': ' + a[6] if a[6] else ''}; {a[7]} codes) | nuproc {b[3]:3d} triples ({b[4]} terms; {b[7]} codes)")
    out.append(f"  total: composition {totals['composition.ttl']} triples, nuproc {totals['nuproc.ttl']} triples")
    out.append(f"  composition_ext.ttl: ad-hoc terms section {rep[('composition_ext.ttl', 'X1')][3]} triples / "
               f"{ext_lines['X1']} lines; code lists {rep[('composition_ext.ttl', 'X2')][3]} triples / "
               f"{ext_lines['X2']} lines")
    out.append(f"  codes used: composition {len(codes_used['composition'])}, nuproc {len(codes_used['nuproc'])}")
    out.append("")
    out.append("VALIDATION")
    for r in val_rows:
        out.append(f"  {r[0]:11s} {r[1]:4s} conforms={r[4]:5s} violations={r[5]} warnings={r[6]} "
                   f"fired=[{r[7]}] constraint_shape_fired={r[8] or '-'} others=[{r[9]}]")
    out.append("")
    out.append("SHAPES PER CONSTRAINT (shapes / lines / triples)")
    for c in ("c1", "c2", "c3", "c4"):
        a, b = sz[("composition", c)], sz[("nuproc", c)]
        out.append(f"  {c} builder writes {a[0]} / {a[1]} / {a[2]}   NuProc ships {b[0]} / {b[1]} / {b[2]}")
    ta = [sum(sz[("composition", c)][i] for c in CONSTRAINTS) for i in range(3)]
    tb = [sum(sz[("nuproc", c)][i] for c in CONSTRAINTS) for i in range(3)]
    out.append(f"  all four: builder writes {ta[0]} / {ta[1]} / {ta[2]}   NuProc ships {tb[0]} / {tb[1]} / {tb[2]}")
    out.append(f"  composition_shapes.ttl counted lines: {counted_lines(texts['composition_shapes.ttl'])}; "
               f"nuproc-shapes.ttl named node shapes: {len(nu_named)}, counted lines: "
               f"{counted_lines(nu_texts[NUPROC_SHAPES])}")
    out.append("")
    out.append("QUERIES (rows / triple patterns / join variables / optional / union / exists / ad-hoc terms / same answer)")
    for r in qm_rows:
        out.append(f"  {r[0]} {r[1]:11s} rows={r[2]} patterns={r[3]} joins={r[6]} optional={r[7]} union={r[8]} "
                   f"exists={r[9]} adhoc=[{r[10]}] same={r[12]}")
    (RES / "summary.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
