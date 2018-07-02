import sys
import json

import pika

if sys.version_info > (3, 0):
    from PIKACHU.utils.py3 import Single
else:
    from PIKACHU.utils.py2 import Single


"""
Plan: 
1. SimpleProducor/SimpleConsumer use direct exchange_type, message durable and acknowledge is enabled.
   SimpleConsumer is synchronous consumer, SimpleAsyncConsumer is asynchronous consumer
2. BroadCaster/Receiver use fanout exchange_type, for a broadcast/receive pattern. 
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
    def __init__(self, url, namespace=None):
        self._url = url
        self._namespace = namespace or "pikachu"

    def __ensure_connection(self):
        if self._connection is None or not self._connection.is_open:
            self._connection = pika.BlockingConnection(pika.URLParameters(self._url))
        return self._connection

    def __ensure_channel(self):
        if self._channel is None or not self._channel.is_open:
            self.__ensure_connection()
            self._channel = self._connection.channel()
        return self._channel

    def put(self, message):
        """
        The put/get or put/listen pattern. Put a message into the queue.
        :message: the message to put in queue, dict.
        """
        assert isinstance(message, dict), "Message only support dict"
        exchange_type = "direct"
        exchange = "{}.{}".format(self._namespace, exchange_type)
        body = json.dumps(message)
        routing_key = queue_name = exchange
        channel = self.__ensure_channel()
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
        channel.queue_declare(queue=queue_name, durable=True)  # make sure the queue is created.
        channel.confirm_delivery()
        return channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2,))

# TODO: BroadCaster, StreamProducor