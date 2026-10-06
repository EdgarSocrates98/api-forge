import neo4j from 'neo4j-driver';

export async function run(session: any, id: string) {
  return session.run('MATCH (n:User) WHERE n.name = "' + id + '" RETURN n LIMIT 1');
}
