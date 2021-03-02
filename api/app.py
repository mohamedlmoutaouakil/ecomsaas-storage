from api.database.db import initialize_db
from api.database.migrations import initialize_migrations
from config import config_by_name
import connexion
from api.cache.redis_cache import initialize_redis

def create_app(config_name):
  # Create flask application instance
  connex_app = connexion.App(__name__, specification_dir='./openapi/')

  # Read specification.yml to configure the endpoints
  connex_app.add_api('openapi.yml')

  app = connex_app.app
  app.config.from_object(config_by_name[config_name])
  initialize_db(app)
  initialize_migrations(app)
  initialize_redis(app)

  return app