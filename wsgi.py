from api.app import create_app

APP_ENV = os.environ.get('APP_ENV', 'dev')
app = create_app(APP_ENV)