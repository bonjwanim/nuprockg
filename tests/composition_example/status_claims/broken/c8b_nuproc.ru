# c8b (NuProc). Vendor Beta is asserted to have taken part in the merged group D: the cluster reports an engagement
# in which Vendor Beta participates.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
PREFIX obo:    <http://purl.obolibrary.org/obo/>
INSERT DATA {
  syn:cluster-D nuproc:reportsEngagement syn:engagement-D .
  syn:engagement-D a nuproc:Engagement ;
      nuproc:concernsCase syn:case ;
      obo:RO_0000057 syn:org-vendor-beta .
}
