from gremlin_python.process.graph_traversal import __


def run(g):
    return (
        g.V()
        .has_label('person')
        .out('knows')
        .limit(25)
        .to_list()
    )
