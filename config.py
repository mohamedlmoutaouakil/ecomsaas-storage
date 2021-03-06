import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'databases', 'dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    S3_BUCKET="ecomsaas-product-images"
    S3_KEY="AKIA44CDV2GNB2HJQYNI"
    S3_SECRET="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"   
    REDIS_URL = 'redis://redis:6379/0'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'databases', 'test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    S3_BUCKET="ecomsaas-product-images"
    S3_KEY="AKIA44CDV2GNB2HJQYNI"
    S3_SECRET="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"
    REDIS_URL = 'redis://:redispass2021@localhost/0'


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)