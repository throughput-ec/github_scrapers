
CALL apoc.periodic.iterate(
  "CALL apoc.load.json('file:///media/sdb/neo4j/import/papersgood.json') YIELD value
   WITH value.good AS papers
   UNWIND papers AS fine
   RETURN fine",
   "MATCH (ty:TYPE {type:'schema:Article'})
   MATCH (tyt:TYPE {type: "TextualBody"})
   MATCH (mv:MOTIVATION) WHERE mv.term="linking"
   MATCH (aty:AGENTTYPE {type:"Person"})
   MATCH (atyc:AGENTTYPE {type:"Software"})
   MATCH (ag:AGENT { id:"0000-0002-2700-4605",
                   name: "Simon Goring"})
   MATCH (awd:OBJECT {AwardID: fine.AwardID})
   WITH fine, ty, tyt, mv, aty, atyc, ag, awd
   MERGE (oa:OBJECT {id: fine.doi,
                journal: fine.pubname,
                authors: fine.authors,
                    url: fine.URL,
                  title: fine.title})
   ON CREATE SET oa.created = timestamp()
   MERGE (oann:OBJECT {value: 'Linked by GeoDeepDive script (http://github.com/throughput-ec/github_scrapers/nsf_deepdive)',
                   highlight: fine.highlight})
   MERGE (ty)<-[:isType]-(oa)
   MERGE (tyt)<-[:isType]-(oann)
   CREATE (oa)<-[:Target]-(a:ANNOTATION { created: timestamp() })
   MERGE (ags:AGENT {name: "Code scrapers",
                     homepage: "https://github.com/throughput-ec/github_scrapers"})
   MERGE (mv)<-[:hasMotivation]-(a)
   MERGE (a)-[:Body]->(oann)
   MERGE (awd)<-[:Target]-(a)
   MERGE (ag)-[:Created {created: timestamp()}]->(a)
   MERGE (ags)-[:Generated {generated: timestamp()}]->(a)
   MERGE (ags)-[:isAgentType]->(atyc)",{papers: papers, batchSize:100, iterateList:true})
   YIELD batches, total
   RETURN batches, total
