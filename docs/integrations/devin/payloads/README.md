# Devin payload catalog

Generate each payload from the repository root. The command emits the complete
`DevinPayload/v1` JSON; keep the output as a local artifact when a transcript or
review record is needed.

## 1. Read-only discovery in CLI

```text
apiforge devin payload "Discover the next API Forge improvement from the persisted case" --surface cli --task-kind discovery --detail-level full
```

Use `/plan` and inspect the proposed route before allowing edits.

## 2. Implementation in Desktop

```text
apiforge devin payload "Implement the approved change with tests and docs" --surface desktop --task-kind implementation --permission-mode normal --detail-level full
```

Paste the generated `prompt` into Devin Desktop Agent Command Center and review
the diff before accepting file changes.

## 3. Verification/review in CLI

```text
apiforge devin payload "Review the current diff and report evidence-backed gaps" --surface cli --task-kind review --detail-level full
```

Run with normal permissions. A reviewer may use the `api-forge-reviewer`
subagent, but a subagent result is not independent verification until API Forge
checks and evidence are recorded.

## 4. Explicit Cloud handoff

```text
apiforge devin payload "Continue the approved task in Devin Cloud" --surface cloud --task-kind handoff --detail-level full
```

Use `/handoff` only after confirming repository, platform, branch and human
approval boundaries. Return with `/pickup` and re-run local verification.
