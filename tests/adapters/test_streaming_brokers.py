from pathlib import Path

from apiforge.adapters.streaming import (
    build_streaming_ir,
    extract_nats,
    extract_pulsar,
    extract_rabbitmq,
)


def test_rabbitmq_nats_and_pulsar_share_streaming_ir(tmp_path: Path) -> None:
    (tmp_path / "broker.py").write_text(
        "import pika\nchannel.basic_publish(exchange='orders', routing_key='created')\n"
        "channel.basic_consume(queue='orders', on_message_callback=handler)\n"
        "import nats\nawait nc.publish('orders.created', payload)\n"
        "import pulsar\nclient.createProducer('orders')\n",
        encoding="utf-8",
    )
    assert build_streaming_ir(extract_rabbitmq(tmp_path), broker="rabbitmq").broker == "rabbitmq"
    assert build_streaming_ir(extract_nats(tmp_path), broker="nats").broker == "nats"
    assert build_streaming_ir(extract_pulsar(tmp_path), broker="pulsar").broker == "pulsar"
