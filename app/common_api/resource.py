from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.resource import *
from app.utils.response_code import *


# 管道列表获取
@api.route('/resource/resources', methods=['GET'])
@jwt_required
def resourcesForUserFetch():
    # 读取基本数据
    info = request.values
    username = get_jwt_identity()

    # 数据库查询
    resourceQuery = Resource.objects(Q(username=username))
    return {'code': RET.OK, 'data': {'items': resourceQuery}}

