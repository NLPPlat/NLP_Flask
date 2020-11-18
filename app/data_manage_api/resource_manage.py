from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import app
from app.models.resource import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.common_utils import *
from app.utils.file_utils import *
from app.utils.time_utils import *


# 资源列表获取
@api.route('/resource/resources', methods=['GET'])
@jwt_required
def resourcesFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    queryResourceName = info.get('resourceName')
    username = get_jwt_identity()

    # 读取过滤器、设置查询项
    usernameFilter = info.getlist('username[]')
    resourceTypeFilter = info.getlist('resourceType[]')
    sort = info.get('sort')

    # 设置查询条件Q
    q = Q(resourceType__in=resourceTypeFilter)
    if len(queryResourceName) > 0:
        q = q & Q(resourceName__icontains=queryResourceName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        q = q & (Q(username__ne=username) | Q(publicity='公开'))

    # 数据库查询
    resourcesList = Resource.objects(q).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page

    return {'code': RET.OK, 'data': {'total': resourcesList.count(), 'items': resourcesList[front:end]}}




# 资源件上传
@api.route('/resource/resources', methods=['POST'])
@jwt_required
def resourceUpload():
    # 读取基本数据
    resourceFile = request.files['file']
    info = request.values
    username = get_jwt_identity()

    # 存储文件
    filename = resourceFile.filename
    fileurl = getFileURL(filename, app)
    resourceFile.save(fileurl)

    # 存入Resource数据库
    resource = Resource(username=username, resourceType=info.get('resourceType'),
                               resourceName=info.get('resourceName'), desc=info.get('desc'),
                               publicity=info.get('publicity'), url=fileurl,datetime=getTime())
    resource.save()
    return "success"
