req, _ := http.NewRequestWithContext(ctx, http.MethodPost, "http://inventory/reserve", nil)
resp, _ := http.Get("http://catalog/items")
