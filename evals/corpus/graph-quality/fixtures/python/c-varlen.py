from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (a:Person)-[:KNOWS*]->(b) RETURN b LIMIT 10')
