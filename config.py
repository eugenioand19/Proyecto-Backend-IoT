from decouple import config
from datetime import timedelta

class Config:
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', 'super_secret_key_change_this_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(config('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(config('JWT_REFRESH_TOKEN_EXPIRES', 86400)))


class DevelopmentConfig(Config):
    DEBUG = True
    DB_USER = config('DB_USER')
    DB_PASSWORD = config('DB_PASSWORD')
    DB_HOST = config('DB_HOST')
    DB_PORT = config('DB_PORT')
    DB_NAME = config('DB_NAME')

    SQLALCHEMY_DATABASE_URI = config('DATA_BASE_URL_PROD','postgresql://default:3Oc0mBxWDPwT@ep-white-sound-a4u4llif.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require')

class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config('DATA_BASE_URL_PROD','postgres://default:u1vIgKtYRp6i@ep-cold-lab-a4al074v-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require')

config = {
    'development': DevelopmentConfig,
    'production' : ProductionConfig
}