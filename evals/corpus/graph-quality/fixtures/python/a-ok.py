import boto3

client = boto3.client('neptune-graph')


def run():
    return client.execute_query(graphIdentifier='g-1', queryString="MATCH (n:airport {region: 'US-AK'}) CALL neptune.algo.pageRank(n, {edgeLabels: ['route']}) YIELD rank RETURN n.code, rank ORDER BY rank DESC LIMIT 10", language='OPEN_CYPHER')
