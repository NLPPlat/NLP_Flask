from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from app import models, files
from app.utils import fileReader


# 训练数据集文件上传
@api.route('/data/train/file', methods=['POST'])
@jwt_required
def upload():
    uploadFile = request.files['file']
    params = request.form
    filename = files.save(uploadFile)
    fileurl = files.url(filename)
    user = models.User.objects(username=get_jwt_identity()).first()
    trainFile = models.OriginalDataset(user=user, taskType=params.get('taskType'), taskName=params.get('taskName'),
                                       desc=params.get('desc'), publicity=params.get('publicity'), originFile=fileurl)
    trainFile.save()
    return "success"
