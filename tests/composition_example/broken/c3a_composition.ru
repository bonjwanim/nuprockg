# c3a (composition). The model coding v3 records both of its plans on one qualified association instead of one
# association per plan.
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX syn:  <https://example.org/syn/>
DELETE DATA {
  syn:activity-role-coding-v3 prov:qualifiedAssociation syn:association-role-coding-v3-prompt .
  syn:association-role-coding-v3-prompt a prov:Association ;
      prov:agent syn:agent-model-m3 ;
      prov:hadPlan syn:plan-prompt-v3 .
} ;
INSERT DATA { syn:association-role-coding-v3-codebook prov:hadPlan syn:plan-prompt-v3 . }
