MATCH (kw:KEYWORD)
WHERE kw.keyword CONTAINS('earth') OR kw.keyword CONTAINS('paleo')
WITH kw
MATCH (db:dataCat)<-[:Body]-(:ANNOTATION)-[:hasKeyword]->(kw)
WITH db
MATCH (cr:codeRepo)<-[:Target]-(:ANNOTATION)-[:Target]->(db)
WHERE NOT EXISTS(cr.meta) AND NOT EXISTS(cr.status)
WITH DISTINCT cr.url AS url, db.name AS name, rand() AS random
ORDER BY random
RETURN url
SKIP toInteger($offset)
LIMIT 20
