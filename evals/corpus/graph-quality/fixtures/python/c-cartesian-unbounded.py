from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (a:P {id: $id}), (b:Q) RETURN a, b')
