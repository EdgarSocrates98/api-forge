import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (a:Person {id: $id})-[:KNOWS]->(b:Person) RETURN count(b)");
    }
}
