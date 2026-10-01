import boto3

client = boto3.client('neptune-graph')


def run():
    return client.execute_query(graphIdentifier='g-1', queryString="CALL neptune.algo.vectors.topKByNode('n1') YIELD node RETURN node", language='OPEN_CYPHER')
