import gremlin from 'gremlin';

export async function run(g: any) {
  return g.V().repeat(out('knows')).emit().limit(10);
}
