import gremlin from 'gremlin';

export async function run(g: any) {
  return g.V().hasLabel('person').out('knows').limit(10).toList();
}
