from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.utils.response_code import RET
from app.utils.venation_utils import *

# 数据脉络获取
@api.route('/venation', methods=['GET'])
@jwt_required
def datasetListFetch():
    # 读取基本数据
    info = request.values
    nodeid = int(info.get('nodeid'))
    type = info.get('type')
    username = get_jwt_identity()

    venation = findALlRelations(type, nodeid)
    return {'code': RET.OK, 'data': {'venation': venation}}
