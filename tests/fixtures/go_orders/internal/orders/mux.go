package orders

import "net/http"

func Mux() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", health)
	mux.Handle("GET /ready", readyHandler{})
	mux.HandleFunc("/legacy", legacy)
}
