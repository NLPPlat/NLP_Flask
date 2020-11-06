from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.task import *
from app.utils.response_code import *
from app.utils.codehub_utils import *


# 任务列表获取
@api.route('/task/tasks', methods=['GET'])
@jwt_required
def tasksFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    querytaskName = info.get('taskName')
    username = get_jwt_identity()

    # 读取过滤器、设置查询项
    taskTypeFilter = info.getlist('taskType[]')
    sort = info.get('sort')

    # 设置查询条件Q
    q = Q(taskType__in=taskTypeFilter) & Q(username=username)
    if len(querytaskName) > 0:
        q = q & Q(taskName__icontains=querytaskName)

    # 数据库查询
    tasksList = Task.objects(q).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page

    return {'code': RET.OK, 'data': {'total': tasksList.count(), 'items': tasksList[front:end]}}
