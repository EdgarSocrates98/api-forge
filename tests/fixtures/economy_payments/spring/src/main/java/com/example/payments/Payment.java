package com.example.payments;

public class Payment {
    private final String paymentId;
    private final String status;
    private final Money amount;

    public Payment(String paymentId, String status, Money amount) {
        this.paymentId = paymentId;
        this.status = status;
        this.amount = amount;
    }

    public Money getAmount() {
        return amount;
    }
}
