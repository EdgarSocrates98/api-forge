import gremlin from 'gremlin';

export async function run(g: any) {
  return g.V().hasLabel('person').repeat(out('knows')).times(3).limit(10);
}
