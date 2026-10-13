package com.example.cache;

import redis.clients.jedis.Jedis;

public class OrderCache {
    private final Jedis jedis = new Jedis("localhost");

    public String get(String id) {
        return jedis.get("order:" + id);
    }

    public void put(String id, String payload) {
        // write without TTL — AF-DATA-002 fires
        jedis.set("order:" + id, payload);
    }
}
