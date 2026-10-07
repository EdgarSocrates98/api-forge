---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "7c9f5d12c723b1b68922ef524361c592f97ccd2c0686490640c212327bc2d4ee"
covers: [StreamingAccessIR/v1, aws.msk.offline-dump]
api_ir:
  input: Java, Go or Python source and optional MSK posture dump
  output: topics, groups, roles, operations and delivery signals
---
# contract

O IR separa sinais observados de garantias de entrega, lag ou throughput que exigem evidência runtime.
