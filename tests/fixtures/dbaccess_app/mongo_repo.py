"""Mongo lab fixture — bounded and unbounded reads, filtered writes."""

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["shop"]
orders = db["orders"]
sessions = db.sessions


def recent_orders():
    return orders.find({"status": "paid"}).limit(50)


def all_orders():
    return orders.find({})


def top_sessions():
    return sessions.find({"active": True}, limit=20)


def purge_all():
    return orders.delete_many({})


def archive(flag):
    return orders.update_many({"archived": True}, {"$set": {"a": 1}})


def count():
    return orders.count_documents({})
