# c1b (composition). The candidate-set reference of engagement A is marked resolved (its two candidates stay).
PREFIX ex:     <https://example.org/ext#>
PREFIX exstat: <https://example.org/ext/status/>
PREFIX syn:    <https://example.org/syn/>
DELETE DATA { syn:reference-A-export ex:resolutionStatus exstat:unresolvable_candidate_set . } ;
INSERT DATA { syn:reference-A-export ex:resolutionStatus exstat:resolved . }
