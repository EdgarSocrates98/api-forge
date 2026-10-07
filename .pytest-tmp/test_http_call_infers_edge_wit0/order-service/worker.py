from kafka import KafkaConsumer

TOPIC = "payment.authorized"
consumer = KafkaConsumer(TOPIC)
for message in consumer.poll():
    print(message)
