class Config(object):
    pass


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    JWT_SECRET_KEY = 'SoftwareForNlp'
    MONGODB_SETTINGS = {
        'db': 'nlpplat'
    }


# 生产环境配置
class ProductionConfig(Config):
    pass


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
