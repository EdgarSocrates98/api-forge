package com.example.payments;

public class PaymentRequest {
    private String customerId;
    private Money amount;
    private String method;
    private String description;
    private String idempotencyKey;

    public Money getAmount() {
        return amount;
    }

    public String getMethod() {
        return method;
    }
}
