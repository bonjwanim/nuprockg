# c5a (NuProc). Group B keeps its occurrence status but loses its final occurrence claim.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
DELETE DATA { syn:cluster-B nuproc:hasFinalOccurrenceClaim syn:occurrence-claim-B . }
