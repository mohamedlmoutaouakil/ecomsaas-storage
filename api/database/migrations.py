
from flask_migrate import Migrate
from api.database.db import db

migrate = Migrate()

def initialize_migrations(app):
  migrate.init_app(app, db)