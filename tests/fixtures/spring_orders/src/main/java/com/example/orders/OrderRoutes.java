package com.example.orders;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.server.RouterFunction;
import org.springframework.web.reactive.function.server.RouterFunctions;
import org.springframework.web.reactive.function.server.ServerResponse;

import static org.springframework.web.reactive.function.server.RequestPredicates.GET;

@Configuration
public class OrderRoutes {

    @Bean
    public RouterFunction<ServerResponse> statusRoute(OrderHandler handler) {
        return RouterFunctions.route(GET("/orders/status"), handler::status);
    }
}
