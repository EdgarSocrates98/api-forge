from SPARQLWrapper import SPARQLWrapper

sparql = SPARQLWrapper('https://neptune.example:8182/sparql')
sparql.setQuery('SELECT ?s WHERE { ?s a <http://example.org/Person> } LIMIT 10')
