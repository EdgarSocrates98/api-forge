from SPARQLWrapper import SPARQLWrapper

sparql = SPARQLWrapper('https://neptune.example:8182/sparql')
sparql.setQuery('SELECT * WHERE { ?s <http://example.org/p>* ?o }')
