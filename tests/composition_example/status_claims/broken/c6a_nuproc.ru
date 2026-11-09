# c6a (NuProc). Group E's identification status is changed to key_based while its final claim still says verified.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
PREFIX eident: <https://w3id.org/nuproc/engagementidentification/>
DELETE DATA { syn:cluster-E nuproc:hasEngagementIdentification eident:verified . } ;
INSERT DATA { syn:cluster-E nuproc:hasEngagementIdentification eident:key_based . }
