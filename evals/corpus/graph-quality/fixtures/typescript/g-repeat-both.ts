import gremlin from 'gremlin';

export async function run(g: any) {
  return g.V().hasLabel('person').repeat(both()).limit(5);
}
