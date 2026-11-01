# c3b (composition). The model coding v3 loses its prompt specification: only the codebook plan remains.
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX syn:  <https://example.org/syn/>
DELETE DATA { syn:activity-role-coding-v3 prov:qualifiedAssociation syn:association-role-coding-v3-prompt . }
