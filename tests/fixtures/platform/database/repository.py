def find_order(connection, order_id: str):
    return connection.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
