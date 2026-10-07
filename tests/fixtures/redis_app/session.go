package session

import (
	"context"

	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()
var rdb = redis.NewClient(&redis.Options{Addr: "localhost:6379"})

func Load(id string) (string, error) {
	return rdb.Get(ctx, "session:"+id).Result()
}

func Store(id string, value string) error {
	// write without TTL — AF-DATA-002 fires
	return rdb.Set(ctx, "session:"+id, value, 0).Err()
}
