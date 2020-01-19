import redis

class Logger:
    """

    """

    def __init__(self, host='localhost', list_name='returns'):
        self.r = redis.Redis(host='localhost')
        self.list_name = list_name

    def update(self, msg):
        self.r.rpush(self.list_name, msg)

    def update_logs(self, msg):
        self.r.rpush('logs', msg)