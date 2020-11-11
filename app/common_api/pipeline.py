from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.pipeline import *
from app.utils.response_code import *


# 管道列表获取
@api.route('/pipeline/pipelines', methods=['GET'])
@jwt_required
def pipelinesForUserFetch():
    # 读取基本数据
    info = request.values
    taskType = info.get('taskType')
    username = get_jwt_identity()

    # 数据库查询
    pipelineQuery = Pipeline.objects(Q(taskType=taskType) & Q(username=username))
    return {'code': RET.OK, 'data': {'items': pipelineQuery}}