package com.example.orders;

import java.util.List;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/v1")
public class OrderController {
    private static final String BASE = "/dynamic";

    @GetMapping("/orders/{order_id}")
    public Order getOrder(String orderId) {
        return null;
    }

    @GetMapping("/orders/")
    public List<Order> listOrders() {
        return List.of();
    }

    @PostMapping("/orders")
    public Order createOrder(Order order) {
        return order;
    }

    @PostMapping("/orders")
    public Order createOrderAgain(Order order) {
        return order;
    }

    @GetMapping(BASE + "/x")
    public String dynamicRoute() {
        return "x";
    }
}
