from gremlin_python.process.graph_traversal import __


def run(g):
    return g.V().repeat(__.out('knows')).emit().limit(10).to_list()
