from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (n) RETURN n LIMIT 5')
