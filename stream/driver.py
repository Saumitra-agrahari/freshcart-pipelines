"""
RabbitMQ Driver Consumer for Rapido/FreshCart Event Streaming.
Usage: python driver.py NAME PATTERN
Example: python driver.py Ravi "bangalore.koramangala.*"
"""
import json
import os
import sys
import pika

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "rapido-dispatch"


def main():
    if len(sys.argv) < 3:
        print("Usage: python driver.py <NAME> <PATTERN>")
        print("Example: python driver.py Ravi 'bangalore.koramangala.*'")
        sys.exit(1)

    driver_name = sys.argv[1]
    binding_pattern = sys.argv[2]

    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare the topic exchange (matching dispatcher)
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

    # Declare a private exclusive temporary queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind queue to exchange using pattern
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=queue_name,
        routing_key=binding_pattern
    )

    print(f"Driver '{driver_name}' listening on pattern '{binding_pattern}' (queue: {queue_name})")
    print("Waiting for dispatch messages. Press Ctrl+C to exit.\n")

    def on_message(ch, method, properties, body):
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception as e:
            print(f"[{driver_name}] ERROR decoding message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        msg_id = payload.get("id", "UNKNOWN")

        # Validation: If message lacks "zone", reject with basic_nack(requeue=False)
        if "zone" not in payload or not payload.get("zone"):
            print(f"[{driver_name}] REJECTED request {msg_id} [key='{method.routing_key}'] -> missing 'zone' field!")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Valid message: print request and send basic_ack
        city = payload.get("city")
        zone = payload.get("zone")
        req_type = payload.get("type")
        ts = payload.get("ts")

        print(f"[{driver_name}] ACCEPTED request {msg_id}: {city} / {zone} / {req_type} (ts={ts}) [key='{method.routing_key}']")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=on_message,
        auto_ack=False
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\nDriver '{driver_name}' shutting down...")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
