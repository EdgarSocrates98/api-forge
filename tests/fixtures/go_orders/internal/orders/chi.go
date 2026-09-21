package orders

import "github.com/go-chi/chi/v5"

func Routes() {
	r := chi.NewRouter()
	r.Get("/orders", listOrders)
	r.Post("/orders", createOrder)
	r.Get("/orders/{id}", getOrder)
	r.Delete("/orders/{id}", deleteOrder)
	r.Route("/admin", func(r chi.Router) {
		r.Get("/stats", adminStats)
	})
}
