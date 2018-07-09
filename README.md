# PIKACHU
a PIKA based, Cuter and more Human rabbitmq queue Utility (´_ゝ`)

## Simple to use
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



# installation

```bash
pip install git+https://github.com/smilefufu/PIKACHU@master
```

