from kafka import KafkaProducer

producer = KafkaProducer()
producer.send("payment.authorized", b"ok")
