def make_exchange_name(namespace, exchange_type):
    return "{}.{}".format(namespace, exchange_type)

def make_channel_name(namespace, exchange_type):
    return "channel_on_{}.{}".format(namespace, exchange_type)

def make_queue_name(namespace, exchange_type):
    return "queue_for_{}.{}".format(namespace, exchange_type)

def make_direct_key(namespace):
    return "key_for_{}.direct".format(namespace)