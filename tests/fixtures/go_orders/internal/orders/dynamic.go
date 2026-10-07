package orders

import "github.com/go-chi/chi/v5"

var computedPath = "/computed"

func Dynamic(r chi.Router, sub chi.Router) {
	r.Get(computedPath, handler)
	r.Mount("/mounted", sub)
}
