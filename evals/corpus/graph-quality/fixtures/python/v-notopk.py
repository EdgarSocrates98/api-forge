import boto3

client = boto3.client('neptune-graph')


def run():
    return client.execute_query(graphIdentifier='g-1', queryString='CALL neptune.algo.vectors.topK.byEmbedding([0.1, 0.2]) YIELD node RETURN node LIMIT 5', language='OPEN_CYPHER')
