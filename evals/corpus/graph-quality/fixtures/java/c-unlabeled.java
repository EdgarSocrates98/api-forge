import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (n) RETURN n LIMIT 5");
    }
}
