import neo4j from 'neo4j-driver';

export async function run(session: any, query: string) {
  return session.run(query, {});
}
