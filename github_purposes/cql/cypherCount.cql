MATCH (cr:codeRepo)
WHERE NOT (EXISTS(cr.meta) OR EXISTS(cr.status))
RETURN COUNT(DISTINCT cr) AS total
