from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (a:Person {id: $id})-[:KNOWS]->(b:Person) RETURN count(b)')
