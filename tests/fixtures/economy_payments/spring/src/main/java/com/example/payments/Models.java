package com.example.payments;

import java.util.Collection;
import java.util.List;

class Money {
    private long amount;
    private String currency;

    public long getAmount() {
        return amount;
    }
}

class RefundRequest {
    private Money amount;
    private String reason;

    public Money getAmount() {
        return amount;
    }
}

record Refund(String refundId, String paymentId, String status, Money amount) {}

record PaymentPage(List<Payment> items, String nextCursor) {
    static PaymentPage slice(Collection<Payment> all, int start, int limit) {
        List<Payment> items = all.stream().skip(start).limit(limit).toList();
        return new PaymentPage(items, null);
    }
}
