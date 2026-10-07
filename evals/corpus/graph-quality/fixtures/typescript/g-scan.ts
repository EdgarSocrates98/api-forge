import gremlin from 'gremlin';

export async function run(g: any) {
  return g.V().valueMap().toList();
}
