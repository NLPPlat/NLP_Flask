from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import config_map

db = MongoEngine()
jwt = JWTManager()


def create_app(config_name):
    """
    :param config_name: str 配置名称：{develop,product}
    :return:
    """
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name))
    # 允许跨域
    CORS(app, supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)

    from app import service_api
    from app import process_manage_api
    app.register_blueprint(service_api.api, url_prefix='/service')
    app.register_blueprint(process_manage_api.api,url_prefix='/process-manage')
    return app
