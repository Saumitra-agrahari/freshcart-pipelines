"""
RabbitMQ Dispatcher for Rapido/FreshCart Event Streaming.
Publishes order requests every 2 seconds to the 'rapido-dispatch' topic exchange.
"""
import json
import os
import random
import time
from datetime import datetime, timezone
import pika

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "rapido-dispatch"

CITIES = ["Bangalore", "Chennai"]
ZONES = {
    "Bangalore": ["koramangala", "indiranagar", "whitefield", "jayanagar"],
    "Chennai": ["tnagar", "whitefield", "velachery", "adyar"]
}
TYPES = ["ride", "food"]


def get_connection():
    params = pika.URLParameters(AMQP_URL)
    return pika.BlockingConnection(params)


def start_dispatcher():
    print(f"Connecting to RabbitMQ broker at {AMQP_URL}...")
    connection = get_connection()
    channel = connection.channel()

    # Declare topic exchange
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    print(f"Declared topic exchange: '{EXCHANGE_NAME}'")
    print("Starting dispatch loop (publishing every 2 seconds). Press Ctrl+C to stop.\n")

    counter = 1
    try:
        while True:
            city = random.choice(CITIES)
            zone = random.choice(ZONES[city])
            order_type = random.choice(TYPES)

            # Build routing key: city.zone.type in lowercase
            routing_key = f"{city.lower()}.{zone.lower()}.{order_type.lower()}"

            # Message payload
            order_id = f"REQ-{counter:04d}"
            ts = datetime.now(timezone.utc).isoformat()

            message = {
                "id": order_id,
                "city": city,
                "type": order_type,
                "ts": ts
            }

            # Constraint: Every 10th message MUST omit the "zone" field
            is_bad_message = (counter % 10 == 0)
            if not is_bad_message:
                message["zone"] = zone
            else:
                print(f"[!] Dispatcher generating test NACK message (omitting zone for {order_id})")

            body = json.dumps(message)
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=pika.DeliveryMode.Transient
                )
            )

            status_note = " (MISSING ZONE)" if is_bad_message else ""
            print(f"[Dispatcher] Published {order_id} -> key='{routing_key}'{status_note}: {message}")

            counter += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nDispatcher stopped by user.")
    finally:
        connection.close()


if __name__ == "__main__":
    start_dispatcher()
