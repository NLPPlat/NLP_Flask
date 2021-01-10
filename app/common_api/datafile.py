from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.utils.dataset_utils import *
from app.utils.permission_utils import *


# 某个数据文件信息更新
@api.route('datafile/datafiles/ID', methods=['PUT'])
@jwt_required
def datafileInfoUpdate():
    # 读取数据文件信息
    info = request.json
    datafileID = info.get('datafileid')
    datafileType = info.get('datafileType')
    infos = info.get('infos')
    username = get_jwt_identity()

    # 查找数据集
    if datafileType == '资源文件':
        datafileQuery = Resource.objects(id=int(datafileID)).first()
    elif datafileType == '算子文件':
        datafileQuery = Operator.objects(id=int(datafileID)).first()
    elif datafileType == '模型文件':
        datafileQuery = BaseModel.objects(id=int(datafileID)).first()
    elif datafileType == '管道文件':
        datafileQuery = Pipeline.objects(id=int(datafileID)).first()
    elif datafileType == '训练模型文件':
        datafileQuery = TrainedModel.objects(id=int(datafileID)).first()
    if not writePermission(datafileQuery, username):
        return noPeimissionReturn()
    for key in infos:
        datafileQuery[key] = infos[key]
        datafileQuery.save()
    return {'code': RET.OK}
