package com.example.orders;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DynamicController {
    private static final String BASE = "/dynamic";

    @GetMapping(BASE + "/x")
    public String dynamic() {
        return "x";
    }
}
