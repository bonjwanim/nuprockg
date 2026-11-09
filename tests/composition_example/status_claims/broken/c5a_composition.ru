# c5a: group B keeps its occurrence status but loses its final occurrence claim (the claim and the link to it).
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX syn:  <https://example.org/syn/>

DELETE WHERE {
  syn:engagement-B prov:wasDerivedFrom syn:claim-B-occurrence .
  syn:claim-B-occurrence ?p ?o .
}
