# c5b (NuProc). Group C's status is changed to occurred while its final claim still says planned.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
PREFIX ostat:  <https://w3id.org/nuproc/occurrencestatus/>
DELETE DATA { syn:cluster-C nuproc:hasOccurrenceStatus ostat:planned . } ;
INSERT DATA { syn:cluster-C nuproc:hasOccurrenceStatus ostat:occurred . }
