import sys
import time
sys.path.append("../")
import PIKACHU
import settings

consumer = PIKACHU.Receiver(settings.amqp, namespace="cctv")
def cb(envelope):
    print("get message:", envelope.message)
ioloop = consumer.subscribe(cb, from_hub="ten")
ioloop.start()
