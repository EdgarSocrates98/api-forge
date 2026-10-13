from gremlin_python.process.graph_traversal import __


def run(g):
    return g.V().has_label('person').repeat(__.both()).limit(5).to_list()
