# MessagingAccessIR/v1

Intermediate representation for SQS, SNS, EventBridge and Kinesis access.
Static signals are separated from runtime delivery guarantees.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `service` | `sqs\|sns\|eventbridge\|kinesis` | yes |
| `provider` | string | no |
| `destinations` | array | no |
| `roles` | array | no |
| `operations` | array | no |
| `reliability_signals` | array | no |
| `unresolved` | array | no |
