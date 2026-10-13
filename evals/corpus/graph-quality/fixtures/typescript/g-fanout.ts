import gremlin from 'gremlin';

export async function run(g: any) {
  return g.V().hasLabel('person').out().toList();
}
