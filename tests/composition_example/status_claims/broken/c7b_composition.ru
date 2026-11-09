# c7b: the export-side reference of group B is resolved to Vendor K (SYN) while its final claim still says Vendor Beta (SYN).
PREFIX gaf: <http://groundedannotationframework.org/gaf#>
PREFIX syn: <https://example.org/syn/>

DELETE { syn:reference-B-export gaf:denotes syn:org-vendor-beta }
INSERT { syn:reference-B-export gaf:denotes syn:org-vendor-k }
WHERE  { syn:reference-B-export gaf:denotes syn:org-vendor-beta }
