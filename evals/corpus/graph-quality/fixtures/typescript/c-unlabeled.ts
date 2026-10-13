import neo4j from 'neo4j-driver';

export async function run(session: any, id: string) {
  return session.run("MATCH (n) RETURN n LIMIT 5");
}
