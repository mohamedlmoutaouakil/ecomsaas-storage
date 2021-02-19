from api.app import create_app
from flask_script import Manager
from flask_migrate import MigrateCommand
from api.database.db import db

manager = Manager(create_app)
manager.add_option("-c", "--config", dest="config_name", required=False)

manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    """Creates the db tables."""
    with manager.app.app_context():
        db.create_all()

if __name__ == '__main__':
    manager.run()