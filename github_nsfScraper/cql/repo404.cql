MATCH (nb:OBJECT)-[:isType]-(:TYPE {type:'schema:CodeRepository'})
WHERE nb.name = $repos
SET nb.errorType = '404 - Not Found'
SET nb.errorDate = timestamp()
