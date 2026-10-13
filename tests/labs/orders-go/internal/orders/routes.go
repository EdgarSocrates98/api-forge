package orders

import "github.com/go-chi/chi/v5"

func dynamicPath() string {
	return "/computed"
}

func Routes(r chi.Router) {
	r.Route("/v1", func(r chi.Router) {
		r.Route("/orders", func(r chi.Router) {
			r.Get("/{order_id}", getOrder)
			r.Get("/", listOrders)
			r.Post("", createOrder)
			r.Post("", createOrderAgain)
			r.Get(dynamicPath(), dynamicRoute)
		})
	})
}
