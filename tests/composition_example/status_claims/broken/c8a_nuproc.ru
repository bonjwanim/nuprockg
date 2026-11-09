# c8a (NuProc). Vendor Beta is asserted to have taken part in the planned group C: the cluster reports an engagement
# in which Vendor Beta participates.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
PREFIX obo:    <http://purl.obolibrary.org/obo/>
INSERT DATA {
  syn:cluster-C nuproc:reportsEngagement syn:engagement-C .
  syn:engagement-C a nuproc:Engagement ;
      nuproc:concernsCase syn:case ;
      obo:RO_0000057 syn:org-vendor-beta .
}
