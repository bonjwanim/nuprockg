# c7a (NuProc). The export-side reference of group E loses its final resolution claim.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
DELETE DATA { syn:reference-E-export nuproc:hasFinalResolutionClaim syn:resolution-claim-E . }
