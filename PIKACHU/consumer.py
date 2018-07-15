import json
import time
import logging

import pika

from PIKACHU import utils

logger = logging.getLogger(__name__)

class Envelope(object):
    def __init__(self, channel, basic_deliver, properties, body):
        self.channel = channel
        self.basic_deliver = basic_deliver
        self.properties = properties
        self.message = json.loads(body)

    def message_read(self):
        """
        acknowledge the queue that the message has been proccessed.
        """
        self.channel.basic_ack(self.basic_deliver.delivery_tag)


class SimpleConsumer(object):
    EXCHANGE_TYPE = "direct"
    def __init__(self, url, namespace=None):
        """
        :url: amqp url to connect to rabbitmq
        :namespace: namespace to distinguish different business
        """
        self._url = url
        self._connection = pika.BlockingConnection(pika.URLParameters(url))
        self._channel = self._connection.channel()
        self._queue_name = utils.make_queue_name(namespace or "pikachu", self.EXCHANGE_TYPE)
        self._channel.queue_declare(self._queue_name, durable=True)
        

    def get(self, max_len=100):
        """
        Get message from queue, 100 messages max by default.
        :max_len: the max message count to get
        :return: list of Envelope
        """
        
        envelopes = []
        for i in range(max_len):
            basic_deliver, properties, body = self._channel.basic_get(self._queue_name)
            if body:
                envelopes.append(Envelope(self._channel, basic_deliver, properties, body))
            else:
                break
        return envelopes
        

class AsyncConsumer(object):
    _connection = None
    _channel = None
    EXCHANGE_TYPE = "direct"
    def __init__(self, url, namespace=None, tornado_mode=False):
        """
        :url: amqp url to connect to rabbitmq
        :namespace: namespace to distinguish different business
        :tornado_mode: if True will share same ioloop with tornado
        """
        self._url = url
        self._namespace = namespace or "pikachu"
        self._tornado_mode = tornado_mode
        self.Connection = pika.TornadoConnection if tornado_mode else pika.SelectConnection

    def _connect(self):
        # TODO: handle connect fail exception, try reconnect.
        return self.Connection(
            pika.URLParameters(self._url),
            on_open_callback=self.__on_connection_open,
            on_close_callback=self.__on_connection_close)

    def _reconnect(self, tried_times=0):
        logger.info("Reconnect, times: {}".format(tried_times))
        if self._connection and self._connection.is_open:
            logger.info("Already connected, abort.")
            return
        if tried_times >= 5:
            logger.info("Reconnect fail! Retry too many times.")
            return
        self._connection = self._connect()
        try:
            if not self._tornado_mode:
                self._connection.ioloop.start()
            else:
                self._connection.add_timeout(tried_times*5, lambda : self._reconnect(tried_times=tried_times+1))
        except pika.exceptions.AMQPConnectionError:
            time.sleep(tried_times*5)
            self._reconnect(tried_times=tried_times+1)


    def __on_connection_close(self, connection, reply_code, reply_text):
        self._channel = None
        logger.info('connection {} closed for reason [{}: {}], reconnect in 5s...'.format(connection, reply_code, reply_text))
        if self._tornado_mode:
            self._connection.add_timeout(5, self._reconnect)
        else:
            time.sleep(5)
            self._reconnect()


    def __on_connection_open(self, connection):
        logger.info("Connected!")
        self._connection = connection
        self._channel = connection.channel(on_open_callback=self._on_channel_open)
        self._channel.add_on_close_callback(self.__on_channel_closed)

    def __on_channel_closed(self, channel, reply_code, reply_text):
        logger.info("Channel {} is closed for readon [{}:{}]".format(channel, reply_code, reply_text))
        # try reopen channel if connection is still open
        if self._connection and self._connection.is_open:
            self._channel = self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel):
        # Inheritors should implement this method to do things after channel open.
        pass


class SimpleAsyncConsumer(AsyncConsumer):
    EXCHANGE_TYPE = "direct"

    def _on_channel_open(self, channel):
        # consumer don't need to declare the exchage or bind queue to exchange
        queue_name = utils.make_queue_name(self._namespace, self.EXCHANGE_TYPE)
        self._channel.queue_declare(self.__on_queue_declareok, queue=queue_name, durable=True)

    def __on_queue_declareok(self, method_frame):
        queue_name = utils.make_queue_name(self._namespace, self.EXCHANGE_TYPE)
        self._consume_tag = self._channel.basic_consume(self.__on_message, queue=queue_name, no_ack=False)

    def __on_message(self, channel, basic_deliver, properties, body):
        message = Envelope(channel, basic_deliver, properties, body)
        self.callback(message)
    
    def start_listen(self, callback_on_message):
        """
        :callback_on_message: on message callback, callback(Envelope), will pass an Envelope object to the callback.
        :return: the ioloop
        """
        self.callback = callback_on_message
        connection = self._connect()
        return connection.ioloop


# TODO: TEST THE CODE!!!
class Receiver(AsyncConsumer):
    EXCHANGE_TYPE = "fanout"

    def _on_channel_open(self, channel):
        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.EXCHANGE_TYPE, durable=True)
        channel.queue_declare(self.__on_queue_declareok, exclusive=True)
        

    def __on_queue_declareok(self, method_frame):
        self._queue_name = method_frame.method.queue
        self._channel.queue_bind(callback=self.__on_bindok, exchange=self.exchange_name, queue=self._queue_name)

    def __on_bindok(self, frame):
        self._channel.basic_consume(self.__on_message, queue=self._queue_name, no_ack=True)

    def __on_message(self, channel, basic_deliver, properties, body):
        message = Envelope(channel, basic_deliver, properties, body)
        self.callback(message)

    def subscribe(self, callback_on_message, from_hub=None):
        """
        Subscribe message from a hub.
        :callback_on_message: on message callback, callback(Envelope), will pass an Envelope object to the callback.
        :from_hub: the message hub name, where the subscriber subscribe message from.
        """
        self.callback = callback_on_message
        self.exchange_name = utils.make_exchange_name(self._namespace, self.EXCHANGE_TYPE, extra=from_hub)
        connection = self._connect()
        return connection.ioloop