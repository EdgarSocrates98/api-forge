from neo4j import GraphDatabase


def run(session, uid):
    return session.run("MATCH (n:User {id: $id}) RETURN n LIMIT 1", id=uid)
