from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import app
from app.models.model import *
from app.utils.file_utils import *
from app.utils.time_utils import *

# 训练模型上传
@api.route('/trainedmodel/trainedmodels', methods=['POST'])
@jwt_required
def trainedmodelUpload():
    # 读取基本数据
    trainedmodelFile = request.files['file']
    info = request.values
    username = get_jwt_identity()

    # 存储文件
    filename = trainedmodelFile.filename
    fileurl = getFileURL(filename, app)
    trainedmodelFile.save(fileurl)

    # 存入Trainedmodel数据库
    trainedmodel = TrainedModel(username=username, platType=info.get('plat'),
                               modelName=info.get('trainedmodelName'), desc=info.get('desc'),
                               publicity=info.get('publicity'), model=fileurl,datetime=getTime())
    trainedmodel.save()
    return "success"

