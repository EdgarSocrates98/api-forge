from SPARQLWrapper import SPARQLWrapper

sparql = SPARQLWrapper('https://neptune.example:8182/sparql')
sparql.setQuery('SELECT (COUNT(?s) AS ?n) WHERE { ?s a <http://example.org/Person> }')
