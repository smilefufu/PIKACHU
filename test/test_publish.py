import sys
sys.path.append("../")
import random

import PIKACHU
import settings

producor = PIKACHU.BroadCaster(settings.amqp, namespace="cctv")
message = dict(news=random.randint(0, 666))
print("publish message {} result: {}".format(message, producor.publish(message, to_hub="ten")))
