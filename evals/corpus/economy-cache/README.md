# Economy-cache corpus

Ten scenarios over `tests/fixtures/economy_payments` (FastAPI and Spring).
Each case warms a capsule selection for every operation, rebuilds without
changes, applies one scripted mutation (`append` and/or `replace`), re-analyzes
and rebuilds again.

| Case | Mutation | Expected invalidation |
|---|---|---|
| fastapi-unchanged | none | none |
| fastapi-unrelated-file | new `app/feature_flags.py` | none |
| fastapi-models | new class appended to `models.py` | none (slices unchanged) |
| fastapi-money-field | `Money.amount` constraint | the four payment operations |
| fastapi-customers-route | `get_customer` body | `GET /customers/{customer_id}` |
| fastapi-test-file | new test in `test_payments.py` | the three operations carrying it |
| fastapi-contract | comment appended to `openapi.yaml` | none (pointer deps) |
| fastapi-contract-operation | `listPayments` operationId | `GET /payments` |
| spring-payment-request | comment after the class | none |
| spring-payment-request-field | new `PaymentRequest` field | `POST /payments` |

Gates (`apiforge evals cache`): warm hit rate 1.0, byte-identical output
versus `--no-cache`, `stale_reuse` empty, invalidation precision and recall
1.0, and `context delta` recall 1.0 against the expected set. `context delta`
maps files conservatively (file level) while the cache probes slices and
JSON pointers, so delta may list more targets than the cache invalidates.
