import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (a:P), (b:Q) RETURN a, b LIMIT 5");
    }
}
