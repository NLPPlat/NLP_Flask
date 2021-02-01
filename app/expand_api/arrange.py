from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.models.arrange import *
from app.utils.permission_utils import *
from app.utils.preprocess_uitls import *

# 部署创建
from ..nlp.batch_process import batchProcessManage


@api.route('/arrange/arranges', methods=['POST'])
@jwt_required
def arrangeCreate():
    # 读取基本数据
    info = request.json
    taskType = info.get('taskType')
    trainedmodelID = info.get('trainedmodel')
    pipelineID = info.get('pipeline')
    arrangeName = info.get('arrangeName')
    publicity = info.get('publicity')
    desc = info.get('desc')
    username = get_jwt_identity()

    arrange = Arrange(username=username, arrangeName=arrangeName, publicity=publicity,
                      taskType=taskType, datetime=getTime(), trainedmodel=str(trainedmodelID), pipeline=str(pipelineID),
                      desc=desc, arrangeStatus='关闭')
    arrange.url = 'http://127.0.0.1:5000/expand/arrange/' + str(arrange.id)
    arrange.save()
    return {'code': RET.OK}


# 某个部署获取
@api.route('/arrange/arranges/ID', methods=['GET'])
@jwt_required
def arrangeFetch():
    # 读取基本数据
    info = request.values
    arrangeID = info.get('arrangeid')
    username = get_jwt_identity()

    # 数据库读取
    arrangeQuery = Arrange.objects(id=int(arrangeID)).first()
    if not writePermission(arrangeQuery, username):
        return noPeimissionReturn()
    data = arrangeQuery
    return {'code': RET.OK, 'data': data}


# 某个部署监控获取
@api.route('/arrange/arrangeMonitors/ID', methods=['GET'])
@jwt_required
def arrangeMonitorFetch():
    # 读取基本数据
    info = request.values
    arrangeID = info.get('arrangeid')
    username = get_jwt_identity()

    arrangeQuery = Arrange.objects(id=int(arrangeID)).first()
    if not writePermission(arrangeQuery, username):
        return noPeimissionReturn()
    arrangeMonitor = ArrangeMonitor.objects(arrange=int(arrangeID))
    dayData = [0] * 31
    hourData = [0] * 24
    curData = 0
    curDay = int(getTimeForDay())
    curHour = int(getTimeForH())
    for index in arrangeMonitor:
        dayData[index.day - 1] = dayData[index.day - 1] + index.count
        if index.day == curDay:
            hourData[index.hour] = hourData[index.hour] + index.count
            if index.hour == curHour:
                curData = index.count
    return {'code': RET.OK, 'data': {'dayData': dayData, 'hourData': hourData, 'curData': curData}}


# 部署调用
@api.route('/arrange/<arrangeID>', methods=['POST'])
@jwt_required
def arrangeInvoke(arrangeID):
    # 读取基本数据
    info = request.json
    vectors = info.get('vectors')
    username = get_jwt_identity()

    arrange = Arrange.objects(id=int(arrangeID)).first()
    if not readPermission(arrange, username):
        return noPeimissionReturn()
    if arrange.arrangeStatus == '关闭':
        return {'code': RET.FORBBIDEN, 'message': '部署未运行！'}
    if arrange.pipeline != '':
        data = dealPipeline(vectors, int(arrange.pipeline))
    if arrange.trainedmodel != '':
        data = batchProcessManage(data, arrange.taskType, int(arrange.trainedmodel), 'false', '', -1)
    hour = int(getTimeForH())
    day = int(getTimeForDay())
    q = Q(arrange=int(arrangeID)) & Q(hour=hour) & Q(day=day)
    arrangeMonitor = ArrangeMonitor.objects(q).first()
    if arrangeMonitor:
        arrangeMonitor.count = arrangeMonitor.count + 1
    else:
        arrangeMonitor = ArrangeMonitor(arrange=int(arrangeID), hour=hour, day=day, count=1)
    arrangeMonitor.save()

    return {'code': RET.OK, 'data': data['vectors']}
