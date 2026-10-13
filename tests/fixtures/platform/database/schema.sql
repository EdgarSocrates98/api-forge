CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
