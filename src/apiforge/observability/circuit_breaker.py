"""Small deterministic circuit breaker for provider read calls."""

from __future__ import annotations

from typing import Literal

from apiforge.contracts.observability import CircuitBreakerEvent, ObservabilityProvider

CircuitState = Literal["closed", "open", "half_open"]


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout_seconds: float,
        provider: ObservabilityProvider,
        emit: object | None = None,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state: CircuitState = "closed"
        self.failures = 0
        self.opened_at: float | None = None
        self.probe_in_flight = False
        self.provider = provider
        self.emit = emit

    def _event(self, kind: str, now: float, network_called: bool) -> None:
        if callable(self.emit):
            self.emit(
                CircuitBreakerEvent(
                    provider=self.provider,
                    kind=kind,
                    state=self.state,
                    occurred_at=now,
                    failure_count=self.failures,
                    network_called=network_called,
                )
            )

    def before_call(self, now: float) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.opened_at is None or now - self.opened_at < self.recovery_timeout_seconds:
                self._event("blocked", now, False)
                return False
            self.state = "half_open"
            self.probe_in_flight = True
            self._event("half_open", now, False)
            return True
        if self.probe_in_flight:
            self._event("blocked", now, False)
            return False
        self.probe_in_flight = True
        return True

    def record_success(self, now: float) -> None:
        was_half_open = self.state == "half_open"
        self.state = "closed"
        self.failures = 0
        self.opened_at = None
        self.probe_in_flight = False
        if was_half_open:
            self._event("recovered", now, True)

    def record_failure(self, now: float) -> None:
        self.probe_in_flight = False
        self.failures += 1
        self._event("failure", now, True)
        if self.state == "half_open" or self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = now
            self._event("opened", now, True)
