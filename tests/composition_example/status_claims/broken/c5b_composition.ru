# c5b: group C's occurrence status is changed to occurred while its final claim still says planned.
PREFIX schema: <https://schema.org/>
PREFIX exocc:  <https://example.org/ext/occurrence/>
PREFIX syn:    <https://example.org/syn/>

DELETE { syn:engagement-C schema:eventStatus exocc:planned }
INSERT { syn:engagement-C schema:eventStatus exocc:occurred }
WHERE  { syn:engagement-C schema:eventStatus exocc:planned }
