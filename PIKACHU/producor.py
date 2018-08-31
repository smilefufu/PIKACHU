import sys
import json
import logging

import pika

if sys.version_info > (3, 0):
    from PIKACHU.utils.py3 import Single
else:
    from PIKACHU.utils.py2 import Single
from PIKACHU import utils
logger = logging.getLogger(__name__)


"""
Plan: 
3. StreamProducor/StreamConsumer use topic exchange_type, suitable for a topic based multi stream
   subscript pattern (one producor, many consumers with filter).
4. Only SimpleConsumer has a synchronous version, other consumer/receiver are all asynchronous, 
   cause only SimpleProducor keeps a durable message queue, so it's consumer can be "get" off and on,
   while asynchronous consumers/receivers can only "listen" in an ioloop. That's why synchronous consumer
   only has a get method while asynchronous ones only have start_listen method.
5. RPC
"""

class Producor(Single):
    """
    Base class for producors.
    """
    _connection = None
    _channel = None

    def __init__(self, url, namespace=None):
        """
        :url: amqp url to connect to rabbitmq
        :namespace: namespace to distinguish different business
        """
        self._url = url
        self._namespace = namespace or "pikachu"
        self.__prepare_channel()

    def __prepare_channel(self):
        self._connection = pika.BlockingConnection(pika.URLParameters(self._url))
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()
        return self._channel

    def _ensure_channel(self):
        if self._connection.is_closed or self._channel.is_closed:
            self.__prepare_channel()
        else:
            # detect server disconnect
            try:
                self._connection.process_data_events()
            except pika.exceptions.ConnectionClosed:
                logger.info("Connection closed by server, try reconnect.")
                self.__prepare_channel()
        return self._channel


class SimpleProducor(Producor):
    """
    SimpleProducor use singleton pattern. Connection to rabbitmq is BlockingConnection. All messages are durable and ack needed.
    """
    EXCHANGE_TYPE = "direct"

    def put(self, message, namespace=None):
        """
        The put/get or put/listen pattern. Put a message into the queue.
        :message: the message to put in queue, dict.
        """
        assert isinstance(message, dict), "Only dict type is supported for a message."
        if namespace is None:
            namespace = self._namespace
        body = json.dumps(message)
        exchange = utils.make_exchange_name(namespace, self.EXCHANGE_TYPE)
        routing_key = utils.make_direct_key(namespace)
        queue_name = utils.make_queue_name(namespace, self.EXCHANGE_TYPE)
        channel = self._ensure_channel()
        channel.exchange_declare(exchange=exchange, exchange_type=self.EXCHANGE_TYPE, durable=True)
        channel.queue_declare(queue=queue_name, durable=True)  # make sure the queue is created.
        binding_key = routing_key  # direct mode only match routing_key with binding_key, they should be the same
        channel.queue_bind(queue_name, exchange, binding_key)
        return channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"))


class BroadCaster(Producor):
    """
    Almost the same as SimpleProducor, the only differences are exchange type is fanout, and routing key is ignored.(for now)
    """
    EXCHANGE_TYPE = "fanout"

    def publish(self, message, to_hub=None):
        """
        Publish a message to all subscribers.
        :message: the message to publish, dict.
        :to_hub: the message hub name, where the publisher publish message to.
        """
        assert isinstance(message, dict), "Only dict type is supported for a message."
        body = json.dumps(message)
        if namespace is None:
            namespace = self._namespace
        exchange = utils.make_exchange_name(namespace, self.EXCHANGE_TYPE, extra=to_hub)
        channel = self._ensure_channel()
        channel.exchange_declare(exchange=exchange, exchange_type=self.EXCHANGE_TYPE, durable=True)
        return channel.basic_publish(exchange=exchange, routing_key="", body=body)

# TODO:  StreamProducor