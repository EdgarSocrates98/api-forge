from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (n) WHERE n.age > 3 RETURN n')
