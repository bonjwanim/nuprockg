# c4 (composition). In SEM a role and the participation are one node (a sem:Role constraint on sem:hasActor whose
# rdf:value is the bearer), so a bearer that does not participate can only be written by detaching that node from the
# engagement: the node keeps its bearer and its role types but no event has it as an actor.
PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
PREFIX syn: <https://example.org/syn/>
DELETE DATA { syn:engagement-B sem:hasActor syn:participation-B-export . }
