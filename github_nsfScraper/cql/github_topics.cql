MERGE (asy:AGENTTYPE {type: "SoftwareAgent"})
MERGE (aty:AGENTTYPE {type:"Person"})
WITH aty, asy
  MATCH (o:OBJECT {id: $id})
  MERGE (ag:AGENT { id:"0000-0002-2700-4605",
                    name: "Simon Goring"}) <-[:isAgentType]-(aty)
  ON CREATE SET ag.created = timestamp()
  MERGE (ags:AGENT {name: "Keyword addition",
                    homepage: "https://github.com/SimonGoring/github_re3scraper"})<-[:isAgentType]-(asy)
  MERGE (o)<-[:Body]-(a:ANNOTATION)-[:Generated]->(ags)
    ON CREATE SET a.created = timestamp()
  MERGE (o)<-[:Body]-(a)-[:Created]->(ag)
  MERGE (mv:MOTIVATION {term: "tagging"})<-[:hasMotivation]-(a)
WITH a, o
  MERGE (dbt:OBJECT {value: "The software repository is tagged with these terms."})
WITH a, o, dbt
  MATCH (typ:TYPE {type: "TextualBody"})
  MERGE (dbt)-[:isType]->(typ)
  MERGE (a)-[:Body]->(dbt)
WITH a, o
  UNWIND $keywords AS kword
    MERGE (knode:KEYWORD {keyword: rTrim(lTrim(tolower(kword)))})
      ON CREATE SET knode.created = timestamp()
    MERGE (a)-[hk:hasKeyword]->(knode)
      ON CREATE SET hk.created = timestamp()
