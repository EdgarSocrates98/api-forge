from neo4j import GraphDatabase


def run(session):
    return session.run("MATCH (n:P) WHERE n.name = 'LIMIT 5' RETURN n")
