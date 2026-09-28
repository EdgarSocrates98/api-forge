package com.example.payments;

import java.util.HashMap;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/payments")
public class PaymentController {

    private final Map<String, Payment> store = new HashMap<>();
    private final Map<String, String> seenKeys = new HashMap<>();

    @GetMapping
    public PaymentPage list(
            @RequestParam(required = false) String cursor,
            @RequestParam(defaultValue = "20") int limit) {
        int start = cursor == null ? 0 : Integer.parseInt(cursor);
        return PaymentPage.slice(store.values(), start, Math.min(limit, 100));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Payment create(
            @RequestBody PaymentRequest request,
            @RequestHeader("Idempotency-Key") String idempotencyKey) {
        if (seenKeys.containsKey(idempotencyKey)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "idempotency conflict");
        }
        String paymentId = String.format("pay_%06d", store.size() + 1);
        Payment payment = new Payment(paymentId, authorize(request), request.getAmount());
        store.put(paymentId, payment);
        seenKeys.put(idempotencyKey, paymentId);
        return payment;
    }

    @GetMapping("/{payment_id}")
    public Payment get(@PathVariable("payment_id") String paymentId) {
        Payment payment = store.get(paymentId);
        if (payment == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "payment not found");
        }
        return payment;
    }

    @PostMapping("/{payment_id}/refunds")
    @ResponseStatus(HttpStatus.CREATED)
    public Refund refund(
            @PathVariable("payment_id") String paymentId,
            @RequestBody RefundRequest request,
            @RequestHeader("Idempotency-Key") String idempotencyKey) {
        Payment payment = store.get(paymentId);
        if (payment == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "payment not found");
        }
        if (request.getAmount().getAmount() > payment.getAmount().getAmount()) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, "refund exceeds payment");
        }
        return new Refund("ref_" + idempotencyKey.substring(0, 8), paymentId, "pending", request.getAmount());
    }

    private String authorize(PaymentRequest request) {
        if (request.getAmount().getAmount() <= 0) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, "amount must be positive");
        }
        return "card".equals(request.getMethod()) ? "authorized" : "pending";
    }
}
