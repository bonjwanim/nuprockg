# c6a: group E's identification status is changed to key_based while its final claim still says verified.
PREFIX adms: <http://www.w3.org/ns/adms#>
PREFIX exid: <https://example.org/ext/identification/>
PREFIX syn:  <https://example.org/syn/>

DELETE { syn:engagement-E adms:status exid:verified }
INSERT { syn:engagement-E adms:status exid:key_based }
WHERE  { syn:engagement-E adms:status exid:verified }
