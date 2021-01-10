from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.models.model import *
from app.utils.permission_utils import *


# 模型保存
@api.route('/model/models/ID', methods=['POST'])
@jwt_required
def modelUpload():
    # 读取基本数据
    info = request.json
    code = info.get('code')
    publicity = info.get('publicity')
    modelID = info.get('modelid')
    modelName = info.get('modelName')
    platType = info.get('platType')
    username = get_jwt_identity()

    if (int(modelID) == -1):
        model = BaseModel(modelName=modelName, username=username,
                          publicity=publicity, code=code, platType=platType)
        modelIDBack = model.id
        model.save()
        return {'code': RET.OK, 'data': {'modelid': modelIDBack}}
    else:
        modelQuery = BaseModel.objects(id=int(modelID)).first()
        if not writePermission(modelQuery, username):
            return noPeimissionReturn()
        modelQuery.modelName = modelName
        modelQuery.publicity = publicity
        modelQuery.code = code
        modelQuery.platType = platType
        modelQuery.save()
        return {'code': RET.OK}
