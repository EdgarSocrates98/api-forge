from neo4j import GraphDatabase


def run(session, uid):
    return session.run(f"MATCH (n:User {{id: '{uid}'}}) RETURN n LIMIT 1")
