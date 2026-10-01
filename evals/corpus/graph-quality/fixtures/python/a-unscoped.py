import boto3

client = boto3.client('neptune-graph')


def run():
    return client.execute_query(graphIdentifier='g-1', queryString="CALL neptune.algo.pageRank.mutate({writeProperty: 'rank'})", language='OPEN_CYPHER')
