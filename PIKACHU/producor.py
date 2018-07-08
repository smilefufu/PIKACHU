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
1. SimpleProducor/SimpleConsumer use direct exchange_type, message durable and acknowledge is enabled.
   SimpleConsumer is synchronous consumer, SimpleAsyncConsumer is asynchronous consumer
2. Publisher/Subscriber use fanout exchange_type, for a publish/subscribe pattern. 
   Message won't resend if an receiver miss or not ack an message.
3. StreamProducor/StreamConsumer use topic exchange_type, suitable for a topic based multi stream
   subscript pattern (one producor, many consumers with filter).
4. Only SimpleConsumer has a synchronous version, other consumer/receiver are all asynchronous, 
   cause only SimpleProducor keeps a durable message queue, so it's consumer can be "get" off and on,
   while asynchronous consumers/receivers can only "listen" in an ioloop. That's why synchronous consumer
   only has a get method while asynchronous ones only have start_listen method.
"""


class SimpleProducor(Single):
    """
    SimpleProducor use singleton pattern. Connection to rabbitmq is BlockingConnection. All messages are durable and ack needed.
    """
    _connection = None
    _channel = None
    EXCHANGE_TYPE = "direct"

    def __init__(self, url, namespace=None):
        self._url = url
        self._namespace = namespace or "pikachu"
        self.__prepare_channel()

    def __prepare_channel(self):
        self._connection = pika.BlockingConnection(pika.URLParameters(self._url))
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()
        return self._channel

    def __ensure_channel(self):
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

    def put(self, message):
        """
        The put/get or put/listen pattern. Put a message into the queue.
        :message: the message to put in queue, dict.
        """
        assert isinstance(message, dict), "Message only support dict"
        body = json.dumps(message)
        exchange = utils.make_exchange_name(self._namespace, self.EXCHANGE_TYPE)
        routing_key = utils.make_direct_key(self._namespace)
        queue_name = utils.make_queue_name(self._namespace, self.EXCHANGE_TYPE)
        channel = self.__ensure_channel()
        channel.exchange_declare(exchange=exchange, exchange_type=self.EXCHANGE_TYPE, durable=True)
        channel.queue_declare(queue=queue_name, durable=True)  # make sure the queue is created.
        binding_key = routing_key  # direct mode only match routing_key with binding_key, they should be the same
        channel.queue_bind(queue_name, exchange, binding_key)
        return channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2,))


# TODO: Publisher, StreamProducor