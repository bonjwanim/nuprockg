# c7b (NuProc). The export-side reference of group B is resolved to Vendor K while its final claim still says Vendor Beta.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX syn:    <https://example.org/syn/>
DELETE DATA { syn:reference-B-export nuproc:resolvedTo syn:org-vendor-beta . } ;
INSERT DATA { syn:reference-B-export nuproc:resolvedTo syn:org-vendor-k . }
