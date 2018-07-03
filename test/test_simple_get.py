import sys
import time
sys.path.append("../")
import PIKACHU
import settings

consumer = PIKACHU.SimpleConsumer(settings.amqp)
envelopes = consumer.get()
print("get {} message".format(len(envelopes)))

for envelope in envelopes:
    print("get message:", envelope.message)
    envelope.message_read()

