"""Independent receipt verification."""

from apiforge.contracts.observability import OperationReceipt


def verify(receipt: OperationReceipt) -> dict[str, object]:
    passed = receipt.status in {"dry_run", "applied", "verified"}
    return {"verdict": "pass" if passed else "fail", "receipt": receipt.model_dump(mode="json"), "evidence": receipt.evidence}
