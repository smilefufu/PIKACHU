import sys
sys.path.append("../")
import random

import PIKACHU
import settings

producor = PIKACHU.SimpleProducor(settings.amqp)
message = dict(data=random.randint(0, 666))
print("put message {} result: {}".format(message, producor.put(message)))
