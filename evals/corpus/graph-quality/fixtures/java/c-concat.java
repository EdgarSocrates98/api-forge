import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (n:User {id: '" + id + "'}) RETURN n");
    }
}
