from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, configure_uploads
from celery import Celery
from config import config_map

db = MongoEngine()
jwt = JWTManager()
files = UploadSet('files')


# 工厂模式创建flask app
def create_app(config_name):
    """
    :param config_name: str 配置名称：{develop,product}
    :return:
    """

    # 创建
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name))

    # 允许跨域
    CORS(app, supports_credentials=True)

    # 初始化
    db.init_app(app)
    jwt.init_app(app)
    configure_uploads(app, files)

    return app



 # 注册蓝图
def register_blueprint(app):
    from app import common_api
    from app import service_api
    from app import process_manage_api
    from app import data_manage_api
    app.register_blueprint(common_api.api, url_prefix='/common')
    app.register_blueprint(service_api.api, url_prefix='/service')
    app.register_blueprint(process_manage_api.api, url_prefix='/process-manage')
    app.register_blueprint(data_manage_api.api, url_prefix='/data-manage')

    return


# 创建celery的工厂函数
def create_celery(app):
    celery = Celery(
        app.import_name,
        # backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']

    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
