import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (n) WHERE n.age > 3 RETURN n");
    }
}
