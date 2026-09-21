package com.example.orders;

import javax.ws.rs.GET;
import javax.ws.rs.Path;

@Path("/health")
public class HealthResource {

    @GET
    public String health() {
        return "ok";
    }
}
