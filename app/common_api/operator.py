from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json
from . import api
from app import models, files
from app.utils.response_code import RET
from app.utils.dataset_utils import copy
from app.utils.file_utils import fileDelete
from app.utils.code_run_utils import codeRunUtil
from app.models.dataset import *
from app.models.venation import *
from app.models.operator import *

# 个人算子列表展示
@api.route('/operator/operators', methods=['GET'])
@jwt_required
def operatorsForUserFetch():
    # 读取基本数据
    info = request.values
    operatorType=info.get('operatorType')
    username = get_jwt_identity()

    # 数据库查询
    operatorQuery = Operator.objects(Q(operatorType=operatorType) & Q(username=username))
    return {'code':RET.OK,'data':{'items':operatorQuery}}