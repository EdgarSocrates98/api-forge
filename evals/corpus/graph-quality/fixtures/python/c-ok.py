from neo4j import GraphDatabase


def run(session):
    return session.run('MATCH (a:Person {id: $id})-[:KNOWS*1..3]->(b:Person) RETURN b LIMIT 10')
