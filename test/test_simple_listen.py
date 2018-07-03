import sys
import time
sys.path.append("../")
import PIKACHU
import settings

consumer = PIKACHU.SimpleAsyncConsumer(settings.amqp)
def cb(envelope):
    print("get message:", envelope.message)
    envelope.message_read()
ioloop = consumer.start_listen(cb)
ioloop.start()
