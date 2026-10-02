# Apache Kafka Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Apache Kafka topics, producers, consumers, consumer groups, and administration. The inherited examples cover KRaft and legacy ZooKeeper deployments; use the documentation for the exact installed release.

## Safety

Confirm the cluster, topic, and consumer group before administration. Formatting storage, deleting topics or groups, changing retention, and resetting offsets can lose data or replay processing. Inspect metadata and lag first, and review a dry run before executing an offset reset.

## Quick reference

### Introduction to Apache Kafka

Apache Kafka is a distributed streaming platform that enables building real-time data pipelines and streaming applications. It is widely used for high-throughput, fault-tolerant messaging, as well as enabling stream processing. Kafka works on the concept of topics, producers, and consumers.

> **Note on Versions**: Kafka 2.8+ introduced KRaft mode (Kafka Raft), which eliminates the dependency on ZooKeeper. Kafka 3.3+ made KRaft production-ready, and ZooKeeper mode is deprecated as of Kafka 3.5+. KRaft is now the recommended deployment mode. Commands that previously used `--zookeeper` now use `--bootstrap-server`.

### Key Concepts

- **Topic**: A category or feed name to which records are published. Topics in Kafka are multi-subscriber.
- **Producer**: An entity that publishes data to Kafka topics.
- **Consumer**: An entity that subscribes to topics and processes the feed of published records.
- **Consumer Group**: A group of consumers that share the workload of consuming from a topic. Each partition is consumed by only one member of the group.
- **Broker**: A Kafka server that stores data and serves clients.
- **Cluster**: A group of Kafka brokers.
- **Partition**: A division of a topic for scalability and parallel processing. Topics can have multiple partitions.
- **Replication Factor**: The number of copies of each partition maintained across brokers for fault tolerance.
- **Offset**: A unique identifier of records within a partition. Consumers track their position using offsets.
- **Leader / Follower**: Each partition has one leader broker and zero or more follower brokers. Followers replicate the leader.
- **ZooKeeper** *(Deprecated)*: Previously used for coordinating and managing Kafka brokers. Replaced by KRaft.
- **KRaft (Kafka Raft)**: Kafka's built-in consensus mechanism that replaces ZooKeeper. Uses a metadata quorum within the Kafka cluster itself.

### KRaft vs ZooKeeper Mode

| Feature | KRaft Mode | ZooKeeper Mode |
|---|---|---|
| External dependency | None | Requires ZooKeeper cluster |
| Recommended since | Kafka 3.3+ | Kafka < 3.5 |
| Status | Current standard | Deprecated (Kafka 3.5+) |
| Metadata storage | Inside Kafka (controller quorum) | Separate ZooKeeper nodes |
| Operational complexity | Lower | Higher |
| Startup command | `kafka-server-start.sh` | `zookeeper-server-start.sh` + `kafka-server-start.sh` |

### Basic Kafka Operations

#### Starting Kafka (KRaft Mode — Recommended)

```bash
# Generate a cluster UUID
KAFKA_CLUSTER_ID="$(kafka-storage.sh random-uuid)"

# Inspect the configured storage paths before formatting; use only a new disposable data directory.
# WARNING: storage formatting changes broker metadata; never reformat existing cluster storage.
# Format the storage directory
kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c /path/to/kraft-server.properties

# Start Kafka
kafka-server-start.sh /path/to/kraft-server.properties
```

#### Starting Kafka (Legacy ZooKeeper Mode — Deprecated)

```bash
# Start ZooKeeper first
zookeeper-server-start.sh config/zookeeper.properties

# Then start Kafka
kafka-server-start.sh config/server.properties
```

#### Topic Management

**Create a Topic**
```bash
# KRaft / Modern Kafka (3.0+)
kafka-topics.sh --create \
  --bootstrap-server <broker-host:port> \
  --replication-factor <number> \
  --partitions <number> \
  --topic <topic-name>

# Legacy (deprecated)
kafka-topics.sh --create \
  --zookeeper <zookeeper-host:port> \
  --replication-factor <number> \
  --partitions <number> \
  --topic <topic-name>
```

**List Topics**
```bash
kafka-topics.sh --list --bootstrap-server <broker-host:port>
```

**Describe a Topic**
```bash
kafka-topics.sh --describe --topic <topic-name> --bootstrap-server <broker-host:port>
```

**Delete a Topic**
```bash
kafka-topics.sh --describe --topic <topic-name> --bootstrap-server <broker-host:port>
# WARNING: deletion removes the topic and its retained data.
kafka-topics.sh --delete --topic <topic-name> --bootstrap-server <broker-host:port>
```

**Alter a Topic (add partitions)**
```bash
kafka-topics.sh --alter --topic <topic-name> --partitions <new-number> --bootstrap-server <broker-host:port>
```

#### Producing Messages

```bash
# Basic console producer
kafka-console-producer.sh --broker-list <broker-list> --topic <topic-name>

# With key-value pairs
kafka-console-producer.sh \
  --broker-list <broker-list> \
  --topic <topic-name> \
  --property "key.separator=:" \
  --property "parse.key=true"
```

#### Consuming Messages

```bash
# Read from beginning
kafka-console-consumer.sh \
  --bootstrap-server <broker-list> \
  --topic <topic-name> \
  --from-beginning

# Read from the latest offset (default)
kafka-console-consumer.sh \
  --bootstrap-server <broker-list> \
  --topic <topic-name>

# Read with keys displayed
kafka-console-consumer.sh \
  --bootstrap-server <broker-list> \
  --topic <topic-name> \
  --from-beginning \
  --property print.key=true \
  --property key.separator=":"

# Limit number of messages consumed
kafka-console-consumer.sh \
  --bootstrap-server <broker-list> \
  --topic <topic-name> \
  --from-beginning \
  --max-messages 100
```

### Advanced Kafka Operations

#### Modifying Topic Configuration

```bash
# Inspect current configuration before altering it.
kafka-configs.sh --bootstrap-server <broker-host:port> --entity-type topics --entity-name <topic-name> --describe
# WARNING: retention changes can remove previously retained records.
# Add/alter a configuration
kafka-configs.sh \
  --bootstrap-server <broker-host:port> \
  --entity-type topics \
  --entity-name <topic-name> \
  --alter \
  --add-config retention.ms=86400000

# Describe topic configs
kafka-configs.sh \
  --bootstrap-server <broker-host:port> \
  --entity-type topics \
  --entity-name <topic-name> \
  --describe

# Inspect current topic configuration before reverting it.
kafka-configs.sh --bootstrap-server <broker-host:port> --entity-type topics --entity-name <topic-name> --describe
# WARNING: inherited retention settings can remove records.
# Delete a config override (revert to broker default)
kafka-configs.sh \
  --bootstrap-server <broker-host:port> \
  --entity-type topics \
  --entity-name <topic-name> \
  --alter \
  --delete-config retention.ms
```

#### Kafka Consumer Groups

```bash
# Consume as part of a named group (enables offset tracking and load sharing)
kafka-console-consumer.sh \
  --bootstrap-server <broker-list> \
  --topic <topic-name> \
  --group <group-name>

# List all consumer groups
kafka-consumer-groups.sh --bootstrap-server <broker-list> --list

# Describe a consumer group (show lag, offsets, members)
kafka-consumer-groups.sh --bootstrap-server <broker-list> --describe --group <group-name>

# Inspect group offsets and lag; stop group consumers and review a dry run before --execute.
kafka-consumer-groups.sh --bootstrap-server <broker-list> --describe --group <group-name>
kafka-consumer-groups.sh --bootstrap-server <broker-list> --group <group-name> --topic <topic-name> --reset-offsets --to-earliest --dry-run
# WARNING: executing this reset can replay records and repeat downstream effects.
# Reset consumer group offsets to beginning
kafka-consumer-groups.sh \
  --bootstrap-server <broker-list> \
  --group <group-name> \
  --topic <topic-name> \
  --reset-offsets \
  --to-earliest \
  --execute

# Review the timestamp reset without changing offsets first.
kafka-consumer-groups.sh --bootstrap-server <broker-list> --group <group-name> --topic <topic-name> --reset-offsets --to-datetime <timestamp> --dry-run
# WARNING: executing this reset changes processing position; stop group consumers first.
# Reset offsets to a specific timestamp
kafka-consumer-groups.sh \
  --bootstrap-server <broker-list> \
  --group <group-name> \
  --topic <topic-name> \
  --reset-offsets \
  --to-datetime <timestamp> \
  --execute

# Inspect the group and confirm that no consumer is using it.
kafka-consumer-groups.sh --bootstrap-server <broker-list> --describe --group <group-name>
# WARNING: deleting the group removes stored offsets.
# Delete a consumer group
kafka-consumer-groups.sh --bootstrap-server <broker-list> --delete --group <group-name>
```

#### Cluster and Broker Management

```bash
# List brokers (KRaft)
kafka-metadata-quorum.sh --bootstrap-server <broker-list> describe --status

# Describe cluster metadata
kafka-metadata-quorum.sh --bootstrap-server <broker-list> describe --replication

# Check broker configs
kafka-configs.sh \
  --bootstrap-server <broker-host:port> \
  --entity-type brokers \
  --entity-name <broker-id> \
  --describe
```

#### Kafka Performance Testing

```bash
# Producer performance test
kafka-producer-perf-test.sh \
  --topic <topic-name> \
  --num-records 1000000 \
  --record-size 1000 \
  --throughput -1 \
  --producer-props bootstrap.servers=<broker-list>

# Consumer performance test
kafka-consumer-perf-test.sh \
  --broker-list <broker-list> \
  --topic <topic-name> \
  --messages 1000000
```

### Kafka Streams

Kafka Streams API allows building stream processing applications directly using Kafka — no separate cluster needed.

Key concepts:
- **KStream**: An unbounded, continuously updating stream of records.
- **KTable**: A changelog stream representing the latest value for each key.
- **GlobalKTable**: A fully replicated KTable available on every instance.
- **Topology**: The processing graph of sources, processors, and sinks.

```java
// Basic Kafka Streams example (Java)
StreamsBuilder builder = new StreamsBuilder();
KStream<String, String> source = builder.stream("input-topic");
source.filter((key, value) -> value.contains("error"))
      .to("error-topic");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

### Kafka Connect

Kafka Connect is a tool for scalably and reliably streaming data between Apache Kafka and other data systems (databases, file systems, cloud storage, etc.).

```bash
# Start Connect in standalone mode
connect-standalone.sh config/connect-standalone.properties config/connector.properties

# Start Connect in distributed mode
connect-distributed.sh config/connect-distributed.properties

# REST API — list connectors
curl http://localhost:8083/connectors

# REST API — create a connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{"name": "my-connector", "config": {...}}'

# REST API — check connector status
curl http://localhost:8083/connectors/<connector-name>/status

# Inspect connector status before deletion.
curl http://localhost:8083/connectors/<connector-name>/status
# WARNING: deleting the connector stops its data pipeline.
# REST API — delete a connector
curl -X DELETE http://localhost:8083/connectors/<connector-name>
```

### Common Configuration Properties

**Producer**
| Property | Description | Example |
|---|---|---|
| `bootstrap.servers` | Broker list | `<broker-host-1>:9092,<broker-host-2>:9092` |
| `acks` | Acknowledgment level | `all` (safest), `1`, `0` |
| `retries` | Number of retries | `3` |
| `compression.type` | Message compression | `gzip`, `snappy`, `lz4` |
| `batch.size` | Batch size in bytes | `16384` |

**Consumer**
| Property | Description | Example |
|---|---|---|
| `bootstrap.servers` | Broker list | `<broker-host-1>:9092,<broker-host-2>:9092` |
| `group.id` | Consumer group ID | `my-consumer-group` |
| `auto.offset.reset` | Offset reset policy | `earliest`, `latest` |
| `enable.auto.commit` | Auto commit offsets | `true`, `false` |
| `max.poll.records` | Max records per poll | `500` |

### Tips for Using Kafka

- **Monitor Consumer Lag**: High consumer lag means your consumers can't keep up with producers. Monitor with `kafka-consumer-groups.sh --describe`.
- **Choose Partition Count Wisely**: Partitions can be increased but not decreased. Plan capacity upfront.
- **Replication Factor**: Use at least 3 for production topics. Set `min.insync.replicas=2` with `acks=all` for durability.
- **Retention Policies**: Set `retention.ms` and `retention.bytes` on topics to control data lifetime.
- **Use KRaft for New Deployments**: Avoid ZooKeeper for any new Kafka cluster; it is deprecated.
- **Security**: Enable TLS for encryption in transit and SASL for authentication in production environments.

## Troubleshooting workflow

1. Confirm the cluster, topic, partitions, consumer group, and failure time.
2. Inspect topic metadata, replica state, group lag, and controller quorum without resetting offsets.
3. Collect broker, controller, producer, and consumer logs with timestamps.
4. Compare client configuration, topic settings, permissions, and broker health with the intended state.
5. Apply the smallest correction; review a dry run before any offset reset and avoid storage reformatting during diagnosis.
6. Verify replica health, lag, and application processing; record changed settings and recovery state.

## Official references

- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
