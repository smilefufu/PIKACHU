import unittest
import sys
import random
sys.path.append("../")

import PIKACHU
import settings

class SimpleCase(unittest.TestCase):
    def test_put_and_get(self):
        message = dict(data=random.randint(0, 666))
        producor = PIKACHU.SimpleProducor(settings.amqp)
        producor.put(message)
        envelopes = PIKACHU.SimpleConsumer(settings.amqp).get()
        self.assertIsNot(envelopes, [], msg="message get fail")
        self.assertEqual(message, envelopes[-1].message)
        for e in envelopes:
            e.message_read()

def main():
    unittest.main()

if __name__ == '__main__':
    main()