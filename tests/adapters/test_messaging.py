from pathlib import Path

from apiforge.adapters.messaging import build_messaging_ir, extract_sqs


def test_sqs_extracts_delivery_and_reliability_signals(tmp_path: Path) -> None:
    (tmp_path / "worker.py").write_text(
        "import boto3\n"
        "sqs = boto3.client('sqs')\n"
        "sqs.send_message(QueueUrl='orders-queue', MessageBody=body)\n"
        "sqs.receive_message(QueueUrl='orders-queue', VisibilityTimeout=30)\n"
        "sqs.delete_message(QueueUrl='orders-queue', ReceiptHandle=handle)\n"
        "# dead_letter redrive_policy and retry\n",
        encoding="utf-8",
    )
    ir = build_messaging_ir(extract_sqs(tmp_path), service="sqs")
    assert "orders-queue" in ir.destinations
    assert set(ir.roles) == {"producer", "consumer"}
    assert {"ack", "retry", "dlq"}.issubset(ir.reliability_signals)
