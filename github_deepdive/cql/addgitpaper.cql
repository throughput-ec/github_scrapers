// This call loads in a large `json` file and then iterates through it
// in batches of 100.
MATCH (tya:TYPE {type:"schema:Article"})
MATCH (tycr:TYPE {type:"schema:CodeRepository"})
MATCH (tyt:TYPE {type: "TextualBody"})
MATCH (mv:MOTIVATION) WHERE mv.term="linking"
MATCH (aty:AGENTTYPE {type:"Person"})
MATCH (atyc:AGENTTYPE {type:"SoftwareAgent"})
MATCH (ag:AGENT { id:"0000-0002-2700-4605",
               name: "Simon Goring"})
MERGE (rep:OBJECT {url: $ghurl})
ON CREATE SET rep.created = timestamp()
WITH tya, tyt, tycr, mv, aty, atyc, ag, rep
MERGE (oa:OBJECT {id: $doi})
ON CREATE SET oa.journal = $pubname, oa.authors = $authors, oa.url = $pprurl, oa.title = $title, oa.created = timestamp()
MERGE (oann:OBJECT {value: "Linked by GeoDeepDive script (http://github.com/throughput-ec/github_scrapers/github_deepdive)",
               highlight: $highlight})
MERGE (tya)<-[:isType]-(oa)
MERGE (tycr)<-[:isType]-(rep)
MERGE (tyt)<-[:isType]-(oann)
CREATE (oa)<-[:Target]-(a:ANNOTATION { created: timestamp() })
MERGE (ags:AGENT {name: "Code scrapers",
                 homepage: "https://github.com/throughput-ec/github_scrapers"})
MERGE (mv)<-[:hasMotivation]-(a)
MERGE (a)-[:Body]->(oann)
MERGE (rep)<-[:Target]-(a)
MERGE (ag)-[:Created {created: timestamp()}]->(a)
MERGE (ags)-[:Generated {generated: timestamp()}]->(a)
MERGE (ags)-[:isAgentType]->(atyc)
