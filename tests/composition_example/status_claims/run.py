#!/usr/bin/env python3
"""Rebuild every result in results/ from the files of this folder and of the parent folder.

    python run.py      # the NuProc modules are read from the ontology/ folder of the repository

The measures are those of the parent folder's run.py, whose functions are reused. All output is sorted and carries no
time stamp, so a re-run gives identical files. The expected answers and the NuProc shapes counted per constraint are
read from PROTOCOL.md, whose sha256 is compared with PROTOCOL.sha256 first.

Steps: (1) triples and terms per section; (2) validation of each extended graph and of each broken variant, and, for
the composition, of the broken variants of the parent folder, since two of its base shapes are replaced here; (3) lines
and triples of the shapes per constraint; (4) Q4 to Q6 on both encodings, compared with the protocol and with each
other; (5) summary.txt.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, URIRef

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
_spec = importlib.util.spec_from_file_location("composition_base", PARENT / "run.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

RES = HERE / "results"
BROKEN = HERE / "broken"
# Base shapes that the extension replaces, and the shapes that replace them.
REPLACED = {"cs:C2_ClaimShape": "cs:C2_ClaimShape_rev", "cs:C3_CodingActivityShape": "cs:C3_CodingActivityShape_rev"}
SECTIONS = ("G", "O", "I", "R", "W")
QUERIES = ("q4", "q5", "q6")
CONSTRAINTS = ("c5", "c6", "c7", "c8")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def register(text: str) -> None:
    """Teach the base functions the prefixes of the new files, and which of them hold codes."""
    for pfx, ns in re.findall(r"^@prefix\s+([\w-]*):\s+<([^>]+)>", text, re.M):
        base.PREFIXES.setdefault(pfx, ns)
        code_ns = ns.startswith("https://example.org/ext/") or (ns.startswith("https://w3id.org/nuproc/")
                                                                 and not ns.endswith("/ns#"))
        if code_ns:
            base.CODE_PREFIXES.add(pfx)


def table_after(protocol: str, marker: str) -> tuple[list[str], list[list[str]]]:
    rows = []
    for ln in protocol[protocol.index(marker):].splitlines():
        if ln.startswith("|"):
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif rows:
            break
    return rows[0], sorted(rows[2:])


def drop_shape(g: Graph, name: str) -> None:
    for t in g.cbd(base.expand(name)):
        g.remove(t)


def main() -> int:
    RES.mkdir(exist_ok=True)
    base.VOCAB.update({"schema": "schema.org", "adms": "ADMS"})

    protocol = read(HERE / "PROTOCOL.md")
    recorded = read(HERE / "PROTOCOL.sha256").split()[0]
    actual = hashlib.sha256((HERE / "PROTOCOL.md").read_bytes()).hexdigest()
    if recorded != actual:
        raise SystemExit("PROTOCOL.md differs from the checksum recorded before the encodings were written")

    # inputs ------------------------------------------------------------------------------------------------------
    own = ["composition_status.ttl", "composition_status_ext.ttl", "composition_status_shapes.ttl", "nuproc_status.ttl"]
    own += [f"{e}_{q}.rq" for q in QUERIES for e in ("composition", "nuproc")]
    texts = {n: read(HERE / n) for n in own}
    parent_names = ["composition.ttl", "composition_ext.ttl", "composition_shapes.ttl", "nuproc.ttl"]
    ptexts = {n: read(PARENT / n) for n in parent_names}
    broken = {p.name: read(p) for p in sorted(BROKEN.glob("*.ru"))}
    parent_broken = {p.name: read(p) for p in sorted((PARENT / "broken").glob("*_composition.ru"))}
    nu_texts, nu_src = {}, {}
    for m in base.NUPROC_MODULES + [base.NUPROC_SHAPES]:
        nu_texts[m], nu_src[m] = base.read_nuproc(m)
    for t in list(texts.values()) + list(ptexts.values()):
        register(t)
    rows = [[n, "this folder", base.sha256(texts[n].encode("utf-8"))] for n in own]
    rows += [[f"broken/{n}", "this folder", base.sha256(t.encode("utf-8"))] for n, t in broken.items()]
    rows += [[n, "parent folder", base.sha256(t.encode("utf-8"))] for n, t in ptexts.items()]
    rows += [[m, nu_src[m], base.sha256(nu_texts[m].encode("utf-8"))] for m in base.NUPROC_MODULES + [base.NUPROC_SHAPES]]
    base.write_csv(RES / "inputs.csv", ["file", "read_from", "sha256"], rows)

    for n in own:
        if n.startswith("composition") and "w3id.org/nuproc" in texts[n]:
            raise SystemExit(f"{n}: the composition uses a NuProc IRI")

    tbox = base.merged(*(base.parse(nu_texts[m]) for m in base.NUPROC_MODULES))
    nu_shapes = base.parse(nu_texts[base.NUPROC_SHAPES])
    ext_all = base.merged(base.parse(ptexts["composition_ext.ttl"]), base.parse(texts["composition_status_ext.ttl"]))
    co_shapes = base.merged(base.parse(ptexts["composition_shapes.ttl"]), base.parse(texts["composition_status_shapes.ttl"]))
    for old in REPLACED:
        drop_shape(co_shapes, old)
    data = {
        "composition": base.merged(base.parse(ptexts["composition.ttl"]), base.parse(texts["composition_status.ttl"]), ext_all),
        "nuproc": base.merged(base.parse(ptexts["nuproc.ttl"]), base.parse(texts["nuproc_status.ttl"]), tbox),
    }
    shapes = {"composition": co_shapes, "nuproc": nu_shapes}

    # 1. representation -------------------------------------------------------------------------------------------
    declared = {
        "nuproc": {base.short(s) for s in tbox.subjects() if isinstance(s, URIRef) and base.short(s).startswith("nuproc:")},
        "ex": {base.short(s) for s in ext_all.subjects() if isinstance(s, URIRef) and base.short(s).startswith("ex:")},
        "obo": {base.short(s) for s in tbox.subjects() if isinstance(s, URIRef) and base.short(s).startswith("obo:")},
    }
    rep_rows, term_rows, totals = base.representation(
        {n: texts[n] for n in ("composition_status.ttl", "nuproc_status.ttl", "composition_status_ext.ttl")}, declared)
    base.write_csv(RES / "representation.csv",
                   ["file", "section", "title", "triples", "published_terms", "adhoc_terms", "adhoc_term_list",
                    "distinct_codes", "codes"], rep_rows)
    base.write_csv(RES / "terms_used.csv", ["file", "term", "kind", "vocabulary", "sections", "uses", "declared"], term_rows)
    undeclared = [r[1] for r in term_rows if r[0] == "nuproc_status.ttl" and r[6] == "NO"]
    if undeclared:
        raise SystemExit(f"nuproc_status.ttl uses terms TBox 0.9.0 does not declare: {undeclared}")

    # 2. validation -----------------------------------------------------------------------------------------------
    nu_map = {}
    for row in table_after(protocol, "| Constraint | Shapes |")[1]:
        nu_map[row[0]] = ["nuproc:" + x for x in re.findall(r"`(\w+)`", row[1])]
    co_map = {c: sorted({base.short(s) for s in base.parse(texts["composition_status_shapes.ttl"]).subjects()
                         if isinstance(s, URIRef) and base.short(s).startswith(f"cs:C{c[1]}_")})
              for c in CONSTRAINTS}
    constraint_shapes = {"composition": co_map, "nuproc": nu_map}
    val_rows, detail_rows = [], []
    for enc in ("composition", "nuproc"):
        variants = [("base", "the extended encoding as written", None, None)]
        variants += [(n.split("_")[0], base.first_comment(t), t, n[:2]) for n, t in broken.items() if n.endswith(f"_{enc}.ru")]
        for variant, desc, upd, c in variants:
            g = data[enc] if upd is None else base.apply_update(data[enc], upd)
            conforms, res = base.run_validation(g, shapes[enc])
            fired = sorted({r[1] for r in res if r[0] == "Violation"})
            n_v = sum(1 for r in res if r[0] == "Violation")
            n_w = sum(1 for r in res if r[0] == "Warning")
            if c is None:
                target, detected, others = "", "", ""
            else:
                expected = set(constraint_shapes[enc][c])
                target, detected = c, "yes" if expected & set(fired) else "NO"
                others = " ".join(s for s in fired if s not in expected)
            val_rows.append([enc, variant, target, desc, str(conforms).lower(), n_v, n_w, " ".join(fired), detected, others])
            for r in res:
                detail_rows.append([enc, variant, *r])
    # the broken variants of the parent folder, on the extended composition, since two base shapes are replaced
    base_map = dict(base.CONSTRAINT_SHAPES["composition"])
    base_map["c2"] = [REPLACED.get(s, s) for s in base_map["c2"]]
    base_map["c3"] = [REPLACED.get(s, s) for s in base_map["c3"]]
    for n, t in parent_broken.items():
        variant, c = n.split("_")[0], n[:2]
        conforms, res = base.run_validation(base.apply_update(data["composition"], t), co_shapes)
        fired = sorted({r[1] for r in res if r[0] == "Violation"})
        expected = set(base_map[c])
        val_rows.append(["composition", "parent:" + variant, c, base.first_comment(t), str(conforms).lower(),
                         sum(1 for r in res if r[0] == "Violation"), sum(1 for r in res if r[0] == "Warning"), " ".join(fired),
                         "yes" if expected & set(fired) else "NO", " ".join(s for s in fired if s not in expected)])
    base.write_csv(RES / "validation.csv",
                   ["encoding", "variant", "constraint", "description", "conforms", "violations", "warnings",
                    "shapes_fired", "constraint_shape_fired", "other_shapes_fired"], val_rows)
    base.write_csv(RES / "validation_details.csv",
                   ["encoding", "variant", "severity", "shape", "focus_node", "path", "value", "message"], detail_rows)

    # 3. shape sizes ----------------------------------------------------------------------------------------------
    size_rows = []
    st = texts["composition_status_shapes.ttl"]
    sg = base.parse(st)
    for c in CONSTRAINTS:
        for name in co_map[c]:
            size_rows.append(["composition", c, name, "builder writes", base.counted_lines(base.shape_block(st, name)),
                              base.cbd_triples(sg, base.expand(name))])
    for old, new in REPLACED.items():
        c = new.split(":")[1][:2].lower()
        size_rows.append(["composition", c, new, "builder rewrites a base shape",
                          base.counted_lines(base.shape_block(st, new)), base.cbd_triples(sg, base.expand(new))])
    shipped = nu_texts[base.NUPROC_SHAPES]
    for c in CONSTRAINTS:
        for name in nu_map[c]:
            size_rows.append(["nuproc", c, name, "shipped with NuProc", base.counted_lines(base.shape_block(shipped, name)),
                              base.cbd_triples(nu_shapes, base.expand(name))])
    base.write_csv(RES / "shapes_size.csv", ["encoding", "constraint", "shape", "who", "lines", "triples"], size_rows)

    # the whole set of shapes the builder of the composition has written once the extension is in force
    pt = ptexts["composition_shapes.ttl"]
    pg = base.parse(pt)
    parent_named = sorted({base.short(s) for s in pg.subjects() if isinstance(s, URIRef) and base.short(s).startswith("cs:C")})
    in_force = [(n, base.counted_lines(base.shape_block(pt, n))) for n in parent_named if n not in REPLACED]
    in_force += [(r[2], r[4]) for r in size_rows if r[0] == "composition"]

    # 4. queries --------------------------------------------------------------------------------------------------
    qm_rows, answers, as_expected = [], {}, {}
    for qn, marker in zip(QUERIES, ("**Q4.**", "**Q5.**", "**Q6.**")):
        expected = table_after(protocol, marker)
        for enc in ("composition", "nuproc"):
            qtext = texts[f"{enc}_{qn}.rq"]
            header, res = base.run_query(data[enc], qtext)
            base.write_csv(RES / f"{qn}_{enc}.csv", header, res)
            answers[(qn, enc)] = (header, res)
            as_expected[(qn, enc)] = (header, res) == expected
            m = base.query_metrics(qtext)
            qm_rows.append([qn, enc, len(res), m["triple_patterns"], m["property_paths"], m["variables"], m["join_variables"],
                            m["optional"], m["union"], m["exists"], m["adhoc_terms"], m["vocabularies"],
                            "yes" if as_expected[(qn, enc)] else "NO"])
        same = answers[(qn, "composition")] == answers[(qn, "nuproc")]
        for r in qm_rows[-2:]:
            r.append("yes" if same else "NO")
    base.write_csv(RES / "query_metrics.csv",
                   ["query", "encoding", "rows", "triple_patterns", "property_paths", "variables", "join_variables",
                    "optional", "union", "exists", "adhoc_terms", "vocabularies", "as_in_protocol", "same_answer_as_other_encoding"],
                   qm_rows)

    # 5. summary --------------------------------------------------------------------------------------------------
    rep = {(r[0], r[1]): r for r in rep_rows}
    sz = defaultdict(lambda: [0, 0, 0])
    for enc, c, name, who, lines, triples in size_rows:
        if who != "builder rewrites a base shape":
            sz[(enc, c)][0] += 1
            sz[(enc, c)][1] += lines
            sz[(enc, c)][2] += triples
    ext_h, ext_secs = base.sections(texts["composition_status_ext.ttl"])
    ext_lines = {sid: base.counted_lines(body) for sid, _, body in ext_secs}
    out = ["Extension: status claims and the assertion rule. The protocol matches its recorded checksum.", ""]
    out.append("REPRESENTATION (triples per section; ad-hoc schema terms; distinct codes)")
    for sid in SECTIONS:
        a, b = rep[("composition_status.ttl", sid)], rep[("nuproc_status.ttl", sid)]
        out.append(f"  {sid} composition {a[3]:3d} triples ({a[5]} ad hoc{': ' + a[6] if a[6] else ''}; {a[7]} codes) | "
                   f"nuproc {b[3]:3d} triples ({b[7]} codes)")
    ca = sum(rep[("composition_status.ttl", s)][3] for s in SECTIONS)
    cb = sum(rep[("nuproc_status.ttl", s)][3] for s in SECTIONS)
    out.append(f"  G to W: composition {ca} triples, nuproc {cb} triples")
    out.append(f"  B0 (composition only, not compared): {rep[('composition_status.ttl', 'B0')][3]} triples")
    all_c = len(base.merged(base.parse(ptexts["composition.ttl"]), base.parse(texts["composition_status.ttl"])))
    all_n = len(base.merged(base.parse(ptexts["nuproc.ttl"]), base.parse(texts["nuproc_status.ttl"])))
    out.append(f"  whole case (data files of the parent folder and of this one): composition {all_c} triples, nuproc {all_n} triples")
    x3, x4 = rep[("composition_status_ext.ttl", "X3")], rep[("composition_status_ext.ttl", "X4")]
    concepts = sorted({base.short(s) for s in base.parse(texts["composition_status_ext.ttl"]).subjects(None, URIRef("http://www.w3.org/2004/02/skos/core#Concept"))})
    out.append(f"  composition_status_ext.ttl: ad-hoc terms section {x3[3]} triples / {ext_lines['X3']} lines; "
               f"code lists {x4[3]} triples / {ext_lines['X4']} lines; new codes {len(concepts)}")
    out.append("")
    out.append("VALIDATION")
    for r in val_rows:
        out.append(f"  {r[0]:11s} {r[1]:11s} conforms={r[4]:5s} violations={r[5]} warnings={r[6]} fired=[{r[7]}] "
                   f"constraint_shape_fired={r[8] or '-'} others=[{r[9]}]")
    out.append("")
    out.append("SHAPES PER CONSTRAINT (shapes / lines / triples)")
    for c in CONSTRAINTS:
        a, b = sz[("composition", c)], sz[("nuproc", c)]
        out.append(f"  {c} builder writes {a[0]} / {a[1]} / {a[2]}   NuProc ships {b[0]} / {b[1]} / {b[2]}")
    new_c = [sum(sz[("composition", c)][i] for c in CONSTRAINTS) for i in range(3)]
    uniq = {r[2]: r for r in size_rows if r[0] == "nuproc"}
    out.append(f"  c5 to c8: builder writes {new_c[0]} / {new_c[1]} / {new_c[2]}   NuProc ships {len(uniq)} distinct shapes / "
               f"{sum(r[4] for r in uniq.values())} / {sum(r[5] for r in uniq.values())}")
    for r in size_rows:
        if r[3] == "builder rewrites a base shape":
            out.append(f"  rewritten base shape: {r[2]}, {r[4]} lines")
    out.append(f"  whole set the builder has written with the extension in force: {len(in_force)} shapes, "
               f"{sum(n for _, n in in_force)} lines (before the extension {len(parent_named)} shapes)")
    out.append("")
    out.append("QUERIES (rows / triple patterns / join variables / optional / union / exists / as in the protocol / same answer)")
    for r in qm_rows:
        out.append(f"  {r[0]} {r[1]:11s} rows={r[2]} patterns={r[3]} joins={r[6]} optional={r[7]} union={r[8]} "
                   f"exists={r[9]} as_in_protocol={r[12]} same={r[13]}")
    (RES / "summary.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
