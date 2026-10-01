from gremlin_python.process.graph_traversal import __


def run(g):
    return g.V().has_label('person').repeat(__.out('knows')).times(3).limit(10).to_list()
