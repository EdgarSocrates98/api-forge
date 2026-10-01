"""DynamoDB lab fixture — bounded query, full scan, plain query."""

import boto3

client = boto3.client("dynamodb")
resource = boto3.resource("dynamodb")
orders = resource.Table("orders")


def get_order(order_id):
    return client.get_item(TableName="orders", Key={"id": {"S": order_id}})


def list_all():
    return client.scan(TableName="orders")


def page():
    return client.scan(TableName="orders", Limit=100)


def by_customer(customer_id):
    return client.query(
        TableName="orders",
        KeyConditionExpression="customer_id = :c",
        ExpressionAttributeValues={":c": {"S": customer_id}},
    )


def loose_query():
    return client.query(TableName="orders")
