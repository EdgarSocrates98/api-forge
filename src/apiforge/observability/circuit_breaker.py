"""Small deterministic circuit breaker for provider read calls."""

from __future__ import annotations

from typing import Literal

CircuitState = Literal["closed", "open", "half_open"]


class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_timeout_seconds: float) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state: CircuitState = "closed"
        self.failures = 0
        self.opened_at: float | None = None
        self.probe_in_flight = False

    def before_call(self, now: float) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.opened_at is None or now - self.opened_at < self.recovery_timeout_seconds:
                return False
            self.state = "half_open"
            self.probe_in_flight = True
            return True
        if self.probe_in_flight:
            return False
        self.probe_in_flight = True
        return True

    def record_success(self) -> None:
        self.state = "closed"
        self.failures = 0
        self.opened_at = None
        self.probe_in_flight = False

    def record_failure(self, now: float) -> None:
        self.probe_in_flight = False
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = now

