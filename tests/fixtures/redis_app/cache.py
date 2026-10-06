import redis

r = redis.Redis(host="localhost", port=6379)


def get_order(order_id: str):
    return r.get(f"order:{order_id}")


def put_order(order_id: str, payload: str):
    # write without TTL — AF-DATA-002 fires
    r.set(f"order:{order_id}", payload)


def put_session(session_id: str, payload: str):
    # TTL visible — AF-DATA-002 stays quiet
    r.setex(f"session:{session_id}", 3600, payload)


def list_keys():
    # KEYS — AF-DATA-001 fires
    return r.keys("*")


def wipe():
    # FLUSHALL — AF-DATA-003 fires
    r.flushall()


def tune():
    # CONFIG — AF-DATA-005 fires
    r.config_set("maxmemory", "2gb")


def debug_tool():
    # DEBUG — AF-DATA-006 fires
    r.debug("sleep", "0.1")


def watch():
    # MONITOR — AF-DATA-007 fires
    return r.monitor()


def snapshot():
    # SAVE — AF-DATA-008 fires
    r.save()


def drop_db():
    # FLUSHDB — AF-DATA-004 fires
    r.flushdb()
