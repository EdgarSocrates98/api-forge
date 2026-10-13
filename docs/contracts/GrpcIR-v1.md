# GrpcIR/v1

`GrpcIR/v1` is the provider-neutral boundary for protobuf source, descriptor enrichment, compatibility, code generation, gateway projections and verification. Every service and RPC has a stable fully-qualified name and every input retains a source digest.

The IR never requires `protoc`, Buf, gRPC runtimes, cloud credentials or network access. Unsupported imports and descriptor features remain explicit in `unresolved`.
