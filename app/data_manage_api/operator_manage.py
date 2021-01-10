from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.models.operator import *
from app.utils.codehub_utils import *
from app.utils.permission_utils import *


# 某个算子保存
@api.route('/operator/operators/ID', methods=['POST'])
@jwt_required
def operatorUpload():
    # 读取基本数据
    info = request.json
    code = info.get('code')
    publicity = info.get('publicity')
    operatorID = info.get('operatorid')
    operatorType = info.get('operatorType')
    operatorName = info.get('operatorName')
    username = get_jwt_identity()

    if (int(operatorID) == -1):
        operator = Operator(operatorType=operatorType, operatorName=operatorName, username=username,
                            publicity=publicity, code=code)
        operatorIDBack = operator.id
        operator.save()
        return {'code': RET.OK, 'data': {'operatorid': operatorIDBack}}
    else:
        operatorQuery = Operator.objects(id=int(operatorID)).first()
        if not writePermission(operatorQuery, username):
            return noPeimissionReturn()
        operatorQuery.operatorType = operatorType
        operatorQuery.operatorName = operatorName
        operatorQuery.publicity = publicity
        operatorQuery.code = code
        operatorQuery.save()
        return {'code': RET.OK}


# 某个算子获取
@api.route('/operator/operators/ID', methods=['GET'])
@jwt_required
def operatorFetch():
    # 读取基本数据
    info = request.values
    operatorID = info.get('operatorid')
    username = get_jwt_identity()

    # 数据库读取
    operatorQuery = Operator.objects(id=int(operatorID)).first()
    if not readPermission(operatorQuery, username):
        return noPeimissionReturn()
    data = operatorQuery
    return {'code': RET.OK, 'data': data}


# 某个算子调试
@api.route('/operator/operators/ID/code', methods=['GET'])
@jwt_required
def codeRun():
    # 读取基本数据
    info = request.values
    code = info.get('code')
    datasetID = info.get('datasetid')
    username = get_jwt_identity()

    # 运行代码
    result = operatorRunUtil(code, datasetID)
    return {'code': RET.OK, 'data': str(result)}
