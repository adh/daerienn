from .toplevel import SessionProvider
import base64
import os

class RedisSessionProvider(SessionProvider):
    __persistent__ = True
    def __init__(self, redis_client, expire=3600, prefix=""):
        self.redis_client = redis_client
        self.expire = expire
        self.prefix = prefix
    def load(self, key):
        return self.redis_client[self.prefix + key]
    def store(self, data, session_id=None):
        if session_id is None:
            session_id = base64.b64encode(os.urandom(24)).decode('ascii')
        self.redis_client[self.prefix + session_id] = data
        self.redis_client.expire(self.prefix + session_id, self.expire)
        return session_id
