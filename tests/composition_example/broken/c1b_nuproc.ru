# c1b (NuProc). The candidate-set reference of engagement A is marked resolved (its two candidates stay).
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX rstat:  <https://w3id.org/nuproc/resolutionstatus/>
PREFIX syn:    <https://example.org/syn/>
DELETE DATA { syn:reference-A-export nuproc:hasResolutionStatus rstat:unresolvable_candidate_set . } ;
INSERT DATA { syn:reference-A-export nuproc:hasResolutionStatus rstat:resolved . }
