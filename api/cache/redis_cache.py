import redis

class RedisCache():
  def __init__(self, app=None, **kwargs):
    self.redis_client = None
    self.provider_kwargs = kwargs
    if app is not None:
      self.init_app(app)

  def init_app(self, app, **kwargs):
    redis_url = app.config.get("REDIS_URL")

    self.provider_kwargs.update(kwargs)
    self.redis_client = redis.StrictRedis.from_url(
      redis_url, **self.provider_kwargs
    )

    app.redis_client = self.redis_client

redis_cache = RedisCache()

def initialize_redis(app):
  redis_cache.init_app(app)