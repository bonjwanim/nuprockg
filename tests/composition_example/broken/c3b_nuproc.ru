# c3b (NuProc). The model coding v3 loses its prompt specification: only the codebook plan remains.
PREFIX nuproc: <https://w3id.org/nuproc/ns#>
PREFIX prov:   <http://www.w3.org/ns/prov#>
PREFIX syn:    <https://example.org/syn/>
DELETE DATA {
  syn:activity-role-coding-v3 prov:qualifiedAssociation syn:association-role-coding-v3-prompt ;
      nuproc:usedPromptSpecification syn:plan-prompt-v3 .
}
