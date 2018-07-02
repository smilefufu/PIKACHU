import json
import pika


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
    def __init__(self, url, namespace="pikachu"):
        self._url = url
        self._connection = pika.BlockingConnection(pika.URLParameters(url))
        self._channel = self._connection.channel()
        exchange_type = "direct"
        self._queue_name = routing_key = exchange = "{}.{}".format(namespace, exchange_type)
        self._channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
        self._queue = self._channel.queue_declare(self._queue_name, durable=True)
        self._channel.queue_bind(self._queue_name, exchange, routing_key)
        

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
        

class SimpleAsyncConsumer(object):
    _connection = None
    _channel = None
    _consume_mode = None
    def __init__(self, url, namespace=None, tornado_mode=False):
        self._url = url
        self._namespace = namespace or "pikachu"
        self.Connection = pika.TornadoConnection if tornado_mode else pika.SelectConnection

    def _connect(self):
        # TODO: handle connect fail exception, try reconnect.
        return self.Connection(
            pika.URLParameters(self._url),
            on_open_callback=self.__on_connection_open,
            on_close_callback=self.__on_connection_close)


    def __on_connection_close(self, connection, reply_code, reply_text):
        self._channel = None
        print('connection closed, reconnect in 3s...')
        self._connection.add_timeout(3, self._connect)

    def __on_message(self, channel, basic_deliver, properties, body):
        message = Envelope(channel, basic_deliver, properties, body)
        self.callback(message)

    def start_listen(self, callback_on_message):
        """
        :callback: on message callback, callback(Envelope), will pass an Envelope object to the callback.
        :return: the ioloop
        """
        self.exchange_type = "topic"
        self.exchange_type = "direct"
        self.exchange = "{}.{}".format(self._namespace, self.exchange_type)
        self.callback = callback_on_message
        connection = self._connect()
        return connection.ioloop

    def __on_connection_open(self, connection):
        self._connection = connection
        self._channel = connection.channel(on_open_callback=self.__on_channel_open)

    def __on_channel_closed(self, channel, reply_code, reply_text):
        print("Channel {} is closed, {}, {}".format(channel, reply_code, reply_text))
        self._connection.close()

    def __on_channel_open(self, channel):
        self._channel.add_on_close_callback(self.__on_channel_closed)
        self._channel.exchange_declare(
            callback=self.__on_exchange_declareok,
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=True)

    def __on_exchange_declareok(self, frame):
        self._channel.queue_declare(self.__on_queue_declareok, durable=True)

    def __on_queue_declareok(self, method_frame):
        self._queue_name = method_frame.method.queue
        routing_key = self.exchange
        self._channel.queue_bind(self.__on_bindok, self._queue_name, self.exchange, routing_key)

    def __on_bindok(self, frame):
        # start consuming
        self._consume_tag = self._channel.basic_consume(self.__on_message, queue=self._queue_name, no_ack=False)

    # def subscript(self, namespace=None, categories=[]):
    #     namespace = 
    #     pass