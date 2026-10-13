from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (a:P), (b:Q) RETURN a, b LIMIT 5')
