"""Built-in adapter registry and capability matrix."""

from apiforge.observability.adapters.datadog import DatadogAdapter
from apiforge.observability.adapters.dynatrace import DynatraceAdapter
from apiforge.observability.protocols import VendorAdapter


def vendor_adapters() -> dict[str, VendorAdapter]:
    return {"datadog": DatadogAdapter(), "dynatrace": DynatraceAdapter()}


def capabilities() -> dict[str, list[dict[str, object]]]:
    return {
        name: [item.model_dump(mode="json") for item in adapter.capabilities()]
        for name, adapter in vendor_adapters().items()
    }
