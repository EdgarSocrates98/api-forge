# Brainstorm: API Forge Devin Desktop / CLI / Cloud integration

Status: ✅ Implemented

## Problem

Devin can operate as a local IDE/CLI agent and can hand work to Cloud, but its
surface-specific commands, permissions and extensibility must not be mistaken
for API Forge evidence or external authorization.

## Direction

Use the existing host-neutral layer and add a Devin-specific payload adapter:

- versioned payloads for Desktop, CLI and Cloud;
- local CLI observation with declared/observed evidence separation;
- repository-native `.devin/` config, skill, reviewer and hooks;
- no Devin SDK/API calls and no mutation from the API Forge core;
- docs and tests covering the official current surface.

## Non-goals

Direct Devin session creation, account authentication, Cloud automation,
external MCP credentials, PR creation and model/version guarantees.
