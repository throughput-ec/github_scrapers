MATCH (cr:codeRepo)
  WHERE cr.url = $url OR cr.id = $id
  SET cr.id = $id
  SET cr.meta = toString($meta)
  SET cr.url = $url
  SET cr.name = $name
  SET cr.status = NULL
  RETURN 'okay'
