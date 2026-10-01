from gremlin_python.process.graph_traversal import __


def run(g):
    return g.V().value_map().to_list()
