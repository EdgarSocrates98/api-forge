# StreamingAccessIR/v1

Intermediate representation for Kafka/MSK/Kinesis producer and consumer
access. It contains only statically observed signals and never asserts broker
health or delivery guarantees without evidence.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `broker` | `kafka\|msk\|kinesis\|rabbitmq\|nats\|pulsar` | yes |
| `provider` | string | no |
| `topics` | array | no |
| `consumer_groups` | array | no |
| `roles` | array | no |
| `operations` | array | no |
| `delivery_signals` | array | no |
| `unresolved` | array | no |

The scanner covers Java, Go and Python source patterns and remains offline.
