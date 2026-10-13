import neo4j from 'neo4j-driver';

export async function run(session: any, id: string) {
  return session.run("MATCH (a:Person {id: $id})-[:KNOWS*1..3]->(b:Person) RETURN b LIMIT 10");
}
