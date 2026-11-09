# c7a: the export-side reference of group E loses its final resolution claim (the reified status and organisation statements and the links to them).
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX syn:  <https://example.org/syn/>

DELETE WHERE {
  syn:reference-E-export prov:wasDerivedFrom ?claim .
  ?claim ?p ?o .
}
