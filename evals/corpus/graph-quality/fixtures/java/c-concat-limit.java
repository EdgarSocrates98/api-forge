import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (n:User) WHERE n.name = '" + id + "' RETURN n LIMIT 1");
    }
}
