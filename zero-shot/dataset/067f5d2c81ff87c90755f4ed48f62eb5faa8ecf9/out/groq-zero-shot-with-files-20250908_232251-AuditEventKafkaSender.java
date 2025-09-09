package com.pinterest.singer.loggingaudit.client;

import com.pinterest.singer.loggingaudit.client.common.LoggingAuditClientMetrics;
import com.pinterest.singer.loggingaudit.thrift.LoggingAuditHeaders;
import com.pinterest.singer.loggingaudit.thrift.LoggingAuditEvent;
import com.pinterest.singer.loggingaudit.thrift.LoggingAuditStage;
import com.pinterest.singer.loggingaudit.thrift.configuration.KafkaSenderConfig;
import com.pinterest.singer.metrics.OpenTsdbMetricConverter;
import com.pinterest.singer.utils.CommonUtils;
import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.common.PartitionInfo;
import org.apache.thrift.TException;
import org.apache.thrift.TSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class AuditEventKafkaSender {

private static final Logger logger = LoggerFactory.getLogger(AuditEventKafkaSender.class);

public void sendAuditEventToKafka(LoggingAuditEvent event) {
// Removed the code that was throwing TTransportException and instead
// use a try block to handle it.
try {
TSerializer serializer = new TSerializer();
LoggingAuditHeaders auditHeaders = serializer.toBinary(event);
KafkaProducer<String, byte[]> producer = new KafkaProducer<>(KafkaSenderConfig.defaultSendConfig());
ProducerRecord<String, byte[]> producerRecord = new ProducerRecord<>(
KafkaSenderConfig.auditEventTopicName(),
event.getStage().getValue(),
event.getEvent().getBytes());
producer.send(producerRecord, new Callback() {
@Override
public void onCompletion(RecordMetadata metadata, Exception exception) {
if (exception != null) {
logger.error("Failed to send audit event to Kafka", exception);
}
}
});
} catch (TTransportException e) {
// Handle TTransportException here
logger.error("Failed to send audit event to Kafka", e);
}
}
}