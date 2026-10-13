# Runtime Migration Knowledge Pack

Offline-first rules for Java, Python and Go runtime migrations. The matrix is
declarative; adapters produce findings and command proposals, while runtime
policy controls execution.

## Evidence policy

- A missing toolchain is a named gap, never a successful build.
- A breaking API contract blocks `DONE`.
- Static findings identify their source path or rule.
- External AWS, database and vendor access is read-only in the MVP.
