class Config(object):
    pass


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    JWT_SECRET_KEY = 'SoftwareForNlp'
    JWT_BLACKLIST_ENABLED=True
    JWT_BLACKLIST_TOKEN_CHECKS=['access']
    JWT_ACCESS_TOKEN_EXPIRES = 10*24*60*60
    MONGODB_SETTINGS = {
        'db': 'nlpplat'
    }
    UPLOADED_FILES_DEST = 'e:/ProjectData/NLPPlat'
    JSON_AS_ASCII=False
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_RESULT_SERIALIZER = 'pickle'
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']



# 生产环境配置
class ProductionConfig(Config):
    pass


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
