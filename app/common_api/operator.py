from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.operator import *
from app.utils.response_code import *



# 算子列表获取
@api.route('/operator/operators', methods=['GET'])
@jwt_required
def operatorsForUserFetch():
    # 读取基本数据
    info = request.values
    operatorType = info.get('operatorType')
    username = get_jwt_identity()

    # 数据库查询
    operatorQuery = Operator.objects(Q(operatorType=operatorType) & Q(username=username))
    return {'code': RET.OK, 'data': {'items': operatorQuery}}
