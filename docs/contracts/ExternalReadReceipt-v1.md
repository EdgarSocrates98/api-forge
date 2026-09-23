# ExternalReadReceipt/v1

`af-external-read-receipt/1` binds one GET-only external observation to a
response hash, observation time and declared freshness window. It is emitted
by the GitHub issues and HTTP health adapters.

It does not prove authorship, permission to mutate, deployment safety, SLO
compliance or application correctness. Verification compares the explicit
`--now` timestamp with `fresh_until`; it never contacts the provider again.
