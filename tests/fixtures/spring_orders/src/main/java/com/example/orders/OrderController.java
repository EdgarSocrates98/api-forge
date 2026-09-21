package com.example.orders;

import java.util.List;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/orders")
public class OrderController {

    @GetMapping
    public List<Order> list() {
        return List.of();
    }

    @GetMapping("/{id}")
    public Order get(@PathVariable String id) {
        return null;
    }

    @PostMapping
    public Order create(@RequestBody Order order) {
        return order;
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) {
    }
}
