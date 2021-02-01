from flask import request, make_response, send_file, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import app
from app.utils.file_utils import *
from app.utils.permission_utils import *


# 资源文件上传
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
                        publicity=info.get('publicity'), url=fileurl, datetime=getTime())
    resource.save()
    return "success"


# 某个资源文件导出
@api.route('/resource/resources/ID/download', methods=['GET'])
@jwt_required
def resourceDownload():
    # 读取数据
    info = request.values
    resourceID = int(info.get('resourceid'))
    username = get_jwt_identity()

    # 文件导出
    resourceQuery = Resource.objects(id=resourceID).first()
    if not readPermission(resourceQuery, username):
        return noPeimissionReturn()
    url = resourceQuery.url
    response = make_response(send_file(url))
    # response.headers['content-disposition'] = url.split('___')[-1]
    response.headers['content-disposition'] = 'file.'+url.split('.')[-1]
    response.headers['Access-Control-Expose-Headers'] = 'content-disposition'
    return response
