import boto3

client = boto3.client('neptune-graph')


def run():
    return client.execute_query(graphIdentifier='g-1', queryString="CALL neptune.algo.wcc({edgeLabels: ['route']}) YIELD node RETURN node LIMIT 10", language='OPEN_CYPHER')
