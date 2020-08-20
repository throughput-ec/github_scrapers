MATCH (ty:TYPE {type: "schema:CodeRepository"})
MATCH (tyt:TYPE {type: "TextualBody"})
MATCH (mv:MOTIVATION) WHERE mv.term="linking"
MATCH (aty:AGENTTYPE {type:"Person"})
MERGE (ob:OBJECT {id: toInteger($ghid),
                  url: $ghurl,
                  description: $ghdescription,
                  name: $ghname})
ON CREATE SET ob.created = timestamp()
WITH ty, tyt, ob, mv, aty
MERGE (ty)<-[:isType]-(ob)
CREATE (ob)<-[:Target]-(a:ANNOTATION { created: timestamp() })
MERGE (mv)<-[:hasMotivation]-(a)
MERGE (a)-[:Body]->(obb:OBJECT {value: "Code repository contains a reference to the NSF Award."})-[:isType]->(tyt)
WITH a, aty
MATCH (ot:OBJECT) WHERE ot.AwardID=$otid
MERGE (ot)<-[:Target]-(a)
WITH a, aty
MERGE (ag:AGENT { id:"0000-0002-2700-4605",
                  name: "Simon Goring"})
ON CREATE SET ag.created = timestamp()
MERGE (ag)<-[:isAgentType]-(aty)
MERGE (ags:AGENT {name: "GitHub code linker",
                  homepage: "https://github.com/throughput-ec/throughputdb"})<-[:isAgentType]- (aty)
WITH a, ag, ags
MERGE (ag)-[:Created {created: timestamp()}]->(a)
MERGE (ags)-[:Generated {generated: timestamp()}]->(a)
