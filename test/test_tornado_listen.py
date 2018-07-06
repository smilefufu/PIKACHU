import sys
import time
import tornado
import tornado.web
sys.path.append("../")
import PIKACHU
import settings


def cb(envelope):
    print("get message:", envelope.message)
    envelope.message_read()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Test!")

application = tornado.web.Application([
    (r"/", IndexHandler),
])
application.listen(8080)
consumer = PIKACHU.SimpleAsyncConsumer(settings.amqp, tornado_mode=True)
consumer.start_listen(cb)
ioloop = tornado.ioloop.IOLoop.current()
ioloop.start()
