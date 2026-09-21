package orders

import "github.com/gin-gonic/gin"

func Gin(router *gin.Engine) {
	router.GET("/ping", ping)
	router.POST("/echo", echo)
}
