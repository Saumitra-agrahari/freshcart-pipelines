# Stream Processing with RabbitMQ Topic Exchange

This folder implements the event streaming pipeline (Part D) simulating real-time dispatch and driver routing using RabbitMQ and `pika`.

---

## 1. Starting a Local RabbitMQ Broker

### Option A: Using Docker (Recommended)
Run a local RabbitMQ container with the management web UI enabled:
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
Management UI available at: `http://localhost:15672` (default user/pass: `guest` / `guest`).

### Option B: Ubuntu / Debian / Colab
```bash
sudo apt-get update && sudo apt-get install -y rabbitmq-server
sudo service rabbitmq-server start
```

### Option C: Cloud Broker (e.g. CloudAMQP Free Plan)
Export your broker connection string:
```bash
# Linux / macOS / Bash
export AMQP_URL="amqps://<username>:<password>@<host>/<vhost>"

# Windows PowerShell
$env:AMQP_URL = "amqps://<username>:<password>@<host>/<vhost>"
```

---

## 2. Running Drivers and Dispatcher

Run each driver in a separate terminal window so they listen concurrently.

### Terminal 1: Driver 1 (Ravi - Koramangala all types)
```bash
python stream/driver.py Ravi "bangalore.koramangala.*"
```

### Terminal 2: Driver 2 (Priya - Indiranagar all types)
```bash
python stream/driver.py Priya "bangalore.indiranagar.*"
```

### Terminal 3: Driver 3 (Arjun - Bangalore rides)
```bash
python stream/driver.py Arjun "bangalore.*.ride"
```

### Terminal 4: Driver 4 (Control - All Bangalore messages)
```bash
python stream/driver.py Control "bangalore.#"
```

### Terminal 5: Dispatcher (Publishes events every 2s)
```bash
python stream/dispatcher.py
```

---

## 3. ACK and NACK Behavior (Part D3)

- **ACK (`basic_ack`)**: Sent by the driver when a received message contains all required fields (`id`, `city`, `zone`, `type`, `ts`).
- **NACK (`basic_nack(requeue=False)`)**: Every 10th message sent by `dispatcher.py` intentionally omits the `"zone"` field. Drivers that match the routing key will receive the payload, detect the missing `"zone"`, print `REJECTED`, and discard the message without requeuing.

---

## 4. Part D1: Routing Table on Paper (Template)

| # | Routing Key | Receiving Queues |
|---|---|---|
| 1 | `bangalore.koramangala.food` | *(student to complete)* |
| 2 | `bangalore.indiranagar.ride` | *(student to complete)* |
| 3 | `bangalore.whitefield.ride` | *(student to complete)* |
| 4 | `chennai.tnagar.food` | *(student to complete)* |
| 5 | `chennai.whitefield.ride` | *(student to complete)* |
| 6 | `bangalore.koramangala` | *(student to complete)* |
