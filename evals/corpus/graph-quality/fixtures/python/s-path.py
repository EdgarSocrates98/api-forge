from SPARQLWrapper import SPARQLWrapper

sparql = SPARQLWrapper('https://neptune.example:8182/sparql')
sparql.setQuery('SELECT ?o WHERE { ?s <http://example.org/knows>+ ?o } LIMIT 10')
