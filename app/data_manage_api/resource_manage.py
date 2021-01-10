from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import app
from app.models.resource import *
from app.utils.file_utils import *
from app.utils.time_utils import *


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
