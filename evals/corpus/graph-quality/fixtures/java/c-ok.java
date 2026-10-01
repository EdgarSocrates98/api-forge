import org.neo4j.driver.Session;

class Q {
    Object run(Session session, String id) {
        return session.run("MATCH (a:Person {id: $id})-[:KNOWS*1..3]->(b:Person) RETURN b LIMIT 10");
    }
}
