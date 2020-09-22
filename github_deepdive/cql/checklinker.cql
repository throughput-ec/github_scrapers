// This call loads in a large `json` file and then iterates through it
// in batches of 100.
MATCH (oann:OBJECT {value: "Linked by GeoDeepDive script (http://github.com/throughput-ec/github_scrapers/github_deepdive)",
               highlight: $highlight})
RETURN COUNT(oann) AS res
