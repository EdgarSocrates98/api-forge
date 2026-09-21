package orders

import "github.com/go-chi/chi/v5"

func Secret(r chi.Router) {
	r.Get("/secret", secret)
}
