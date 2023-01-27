# PIKACHU
a PIKA based, Cuter and more Human rabbitmq queue Utility (´_ゝ`)

## Quick peek
### put a message into queue(independent by namespace):
```python
import PIKACHU
PIKACHU.SimpleProducor("amqp://localhost").put(dict(data="some message"))
```

### get some messages from queue:

```python
for envelope in PIKACHU.SimpleConsumer("amqp://localhost").get():
    print("get message:", envelope.message)
    envelope.message_read()
```

### use listener to listen message arrival constantly:

```python
def callback(envelope):
    print("get message:", envelope.message)
    envelope.message_read()
    
consumer = PIKACHU.SimpleAsyncConsumer(settings.amqp)
ioloop = consumer.start_listen(callback)
ioloop.start()
```



# Installation

```bash
pip install git+https://github.com/smilefufu/PIKACHU@master
```
or from pypi
```bash
pip install PI-KA-CHU
```

# Main idea

PIKACHU focus on the business scene of message queue, so users don't have to know the detail concept of rabbitmq, like exchange, exchange type, binding keys... They just have to know what pattern of queue they need to get their bussiness done, and choose it from PIKACHU. That's all.

So PIKACHU plans to provide some common used queue patterns in the human way :) Like the basic pattern put/listen and put/get. Also the publish/subscribe pattern. And other patterns is also in schedule.

### PIKACHU.Producer

The base class of all producers. All producers share the same instantiate method with two basic parameters:

- url:  The amqp string to connect to rabbitmq
- namespace: Namespace for different business. Non-necessary paramter, default value is "pikachu".

### PIKACHU.AsyncConsumer

The base class of all async consumer. Considering nearly all business scene need an async consumer so all consumer in PIKACHU are async consumer, except SimpleConsumer which provides ***get*** method. Prameters:

- url:  The amqp string to connect to rabbitmq
- namespace: Namespace for different business. Non-necessary paramter, default value is "pikachu".
- tornado_mode: If True, the consumer will use pika.TornadoConnection, which use same ioloop as tornado. Default value is False, a pika.SelectConnection is used, so PIKACHU has it's own ioloop, users have to merge their ioloop with PIKACHU's ioloop if they have one.

### PIKACHU.SimpleConsumer

Same parameters as PIKACHU.Producer

# Docs

todo: finish the damn doc

# Examples

### put/get pattern

producor code:

```python
import PIKACHU
producor = PIKACHU.SimpleProducor("amqp://localhost")
message = dict(content="some message")
producor.put(message)
```

consmer code (gets 10 messages max every time it runs):

```python
import PIKACHU
consumer = PIKACHU.SimpleConsumer("amqp://localhost")
for envelope in consumer.get(max_len=10):
    print("get message with content:", envelope.message["conent"])
    envelope.message_read()  # mark message as read, it's necessary in put/get or put/listen pattern. If you miss it, all unmarked message will be delivered again next time you start your consumer.
```

### put/listen pattern

producor code (same as put/get pattern)

consumer code (wait and listen the messages):

```python
import PIKACHU
def callback(envelope):
    print("get message with content:", envelope.message["content"])
    envelope.message_read()
    
consumer = PIKACHU.SimpleAsyncConsumer(settings.amqp)
ioloop = consumer.start_listen(callback)
ioloop.start()  # start the loop to keep the process running
```

### publish/subscribe pattern

publisher code:

```python
import PIKACHU
publisher = PIKACHU.BroadCaster("amqp://localhost")
message = dict(news="today's news")
publisher.publish(message, to_hub="ten")
```

subscriber code:

```python
import PIKACHU
subscriber = PIKACHU.Receiver("amqp://localhost")
def cb(envelope):
    print("get news:", envelope.message["news"])
ioloop = subscriber.subscribe(cb, from_hub="ten")
ioloop.start()  # start the loop to keep the process running
```











