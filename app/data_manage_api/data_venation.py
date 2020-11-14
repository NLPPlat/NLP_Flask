from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app.utils.response_code import RET
from app.utils.file_utils import fileDelete
from app.utils.venation_utils import *
from app.models.dataset import *
from app.models.venation import *


# 数据脉络获取
@api.route('/venation', methods=['GET'])
@jwt_required
def datasetListFetch():
    # 读取基本数据
    info = request.values
    nodeid = int(info.get('nodeid'))
    type = info.get('type')
    username = get_jwt_identity()

    venation=findALlRelations(type,nodeid)
    return {'code': RET.OK, 'data': {'venation': venation}}
