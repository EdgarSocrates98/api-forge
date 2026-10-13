package com.example.payments;

import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;
import org.springframework.web.server.ResponseStatusException;

class PaymentControllerTest {

    private final PaymentController controller = new PaymentController();

    @Test
    void getUnknownPaymentIsNotFound() {
        assertThrows(ResponseStatusException.class, () -> controller.get("pay_missing"));
    }

    @Test
    void refundUnknownPaymentIsNotFound() {
        assertThrows(
                ResponseStatusException.class,
                () -> controller.refund("pay_missing", new RefundRequest(), "key-00000001"));
    }
}
