import neo4j from 'neo4j-driver';

export async function run(session: any, id: string) {
  return session.run("MATCH (n) WHERE n.age > 3 RETURN n");
}
