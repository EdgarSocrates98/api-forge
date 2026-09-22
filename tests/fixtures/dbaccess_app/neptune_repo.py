"""Neptune lab fixture — gremlin traversal and openCypher strings."""

import boto3
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

client = boto3.client("neptunedata")
g = traversal().withRemote(DriverRemoteConnection("wss://x", "g"))


def followers(user_id):
    return g.V().has("user", "id", user_id).out("follows").limit(25)


def everything():
    return g.V().valueMap()


def cypher():
    return client.execute_open_cypher_query(openCypherQuery="MATCH (u:User) RETURN u LIMIT 10")


def cypher_unbounded():
    return client.execute_open_cypher_query(
        openCypherQuery="MATCH (u:User)-[:FOLLOWS]->(f) RETURN f"
    )
