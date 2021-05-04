MATCH (cr:codeRepo)
  WHERE NOT EXISTS(cr.meta)
  WITH DISTINCT cr.url AS url, rand() AS random
  ORDER BY random
  RETURN url
  SKIP toInteger($offset)
  LIMIT 20
