MATCH (cr:codeRepo)
WHERE cr.url = $url
SET cr.status = 404
RETURN 'okay'
