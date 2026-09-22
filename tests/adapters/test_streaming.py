from pathlib import Path

from apiforge.adapters.streaming import build_streaming_ir, extract_kafka, extract_msk_access


def _project(tmp_path: Path) -> Path:
    (tmp_path / "consumer.py").write_text(
        "from kafka import KafkaConsumer\n"
        "consumer = KafkaConsumer('orders', group_id='orders-workers')\n"
        "consumer.commit()\n",
        encoding="utf-8",
    )
    (tmp_path / "producer.go").write_text(
        'import "github.com/segmentio/kafka-go"\n'
        'writer.WriteMessages(ctx, kafka.Message{Topic: "orders"})\n',
        encoding="utf-8",
    )
    return tmp_path


def test_kafka_extracts_topic_group_consumer_and_commit(tmp_path: Path) -> None:
    inventory = extract_kafka(_project(tmp_path))
    ir = build_streaming_ir(inventory)
    assert "orders" in ir.topics
    assert "orders-workers" in ir.consumer_groups
    assert "consumer" in ir.roles
    assert "commit" in ir.delivery_signals


def test_msk_uses_same_contract_with_provider_boundary(tmp_path: Path) -> None:
    ir = build_streaming_ir(
        extract_msk_access(_project(tmp_path)), broker="msk", provider="aws-msk"
    )
    assert ir.broker == "msk"
    assert ir.provider == "aws-msk"
