from neo4j import GraphDatabase


def run(session, uid):
    return session.run("MATCH (n:User {{id: '{}'}}) RETURN n".format(uid))
