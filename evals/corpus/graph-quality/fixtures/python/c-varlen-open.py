from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (a:Person)-[:KNOWS*2..]->(b) RETURN b')
