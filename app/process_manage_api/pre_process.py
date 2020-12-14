from flask import request, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery, app
from app.nlp import preprocess
from app.models.dataset import *
from app.models.operator import *
from app.models.resource import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.codehub_utils import *
from app.utils.file_utils import *
from app.utils.preprocess_uitls import *


# 某个数据集预处理列表获取
@api.route('/pre-process/datasets/ID/preprocesses', methods=['GET'])
@jwt_required
def preprocessStatusFetch():
    # 读取数据
    info = request.values
    datasetID = info.get('datasetid')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and (username == datasetQuery.username or datasetQuery.publicity == '公开'):
        return {'code': RET.OK, 'data': {'items': datasetQuery.preprocessStatus}}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集新增预处理步骤
@api.route('/pre-process/datasets/ID/preprocesses', methods=['POST'])
@jwt_required
def preprocessAdd():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessAdd = info.get('preprocessAdd')
    previousProcessID = int(info.get('previousProcessID'))
    sparkSupport = info.get('sparkSupport')
    preprocessParams = info.get('preprocessParams')
    username = get_jwt_identity()

    # 数据库查询并修改
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        previousID = datasetQuery.preprocessStatus[-1]['id']
        datasetQuery.preprocessStatus.append(
            {'id': previousID + 1, 'preprocessName': preprocessAdd[1], 'preprocessType': preprocessAdd[0],
             'previousProcessID': previousProcessID, 'sparkSupport': sparkSupport, 'preprocessStatus': '未开始',
             'preprocessParams': preprocessParams})
        datasetQuery.save()
        return {'code': RET.OK}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集某个预处理向量查看
@api.route('/pre-process/datasets/ID/preprocesses/ID/vectors', methods=['GET'])
@jwt_required
def preprocessVectorsFetch():
    # 读取数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    preprocessID = int(info.get('preprocessid'))
    username = get_jwt_identity()

    # 分页
    limit = int(info.get('limit'))
    page = int(info.get('page'))

    # 读取数据库
    datasetQuery = PreprocessDataset.objects(id=datasetID).first()
    if datasetQuery and (username == datasetQuery.username or datasetQuery.publicity == '公开'):
        count, vectors = vectors_select_divide_preprocess(datasetID, preprocessID, limit, page)
        return {'code': RET.OK, 'data': {'items': vectors, 'total': count}}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集某个预处理步骤数据查看
@api.route('/pre-process/datasets/ID/preprocesses/ID/data', methods=['GET'])
@jwt_required
def preprocessDataFetch():
    # 读取数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    preprocessID = int(info.get('preprocessid'))
    username = get_jwt_identity()

    # 读取数据库
    datasetQuery = PreprocessDataset.objects(id=datasetID).first()
    if datasetQuery and (username == datasetQuery.username or datasetQuery.publicity == '公开'):
        preprocessObj = getDataForFront(datasetQuery, preprocessID)
        return {'code': RET.OK, 'data': {'preprocessObj': preprocessObj}}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集某个预处理向量修改
@api.route('/pre-process/datasets/ID/preprocesses/ID/data', methods=['POST'])
@jwt_required
def preprocessUpload():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    preprocessID = int(info.get('preprocessid'))
    nature = info.get('nature')
    resourceSelect = info.get('resourceSelect')
    username = get_jwt_identity()

    datasetQuery = PreprocessDataset.objects(id=datasetID).first()
    preprocessObj = datasetQuery.data.filter(id=preprocessID).first()
    if datasetQuery and username == datasetQuery.username:
        if resourceSelect == '':
            file = request.files['file']
            filename = file.filename
            fileurl = getFileURL(filename, app)
            file.save(fileurl)
            preprocessObj[nature] = fileurl
            datasetQuery.save()
        else:
            resource = Resource.objects(id=int(resourceSelect)).first()
            preprocessObj[nature] = resource.url
            datasetQuery.save()
        return {'code': RET.OK}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集某个预处理数据导出
@api.route('/pre-process/datasets/ID/preprocesses/ID/download', methods=['GET'])
@jwt_required
def preprocessDownload():
    # 读取数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    preprocessID = int(info.get('preprocessid'))
    content = info.get('content')
    username = get_jwt_identity()

    # 文件导出
    datasetQuery = PreprocessDataset.objects(id=datasetID).first()
    if datasetQuery and (username == datasetQuery.username or datasetQuery.publicity == '公开'):
        data = getDataFromPreprocessDataset(datasetQuery, preprocessID)
        url = downloadRUL(data, content)
        response = make_response(send_file(url))
        response.headers['content-disposition'] = url.split('___')[-1]
        response.headers['Access-Control-Expose-Headers'] = 'content-disposition'
        return response
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集执行某个预处理步骤
@api.route('/pre-process/datasets/ID/preprocesses/ID/status', methods=['PUT'])
@jwt_required
def preprocessDeal():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessIndex = info.get('preprocessIndex')
    username = get_jwt_identity()

    # 数据库查询修改、异步处理任务
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        preprocessManage.delay(datasetQuery, preprocessIndex)
        return {'code': RET.OK}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 预处理控制层
@celery.task
def preprocessManage(dataset, preprocessIndex):
    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '执行中'
    dataset.save()

    # 步骤、参数读取
    previousProcessIndex = dataset.preprocessStatus[preprocessIndex]['previousProcessID']
    preprocessName = dataset.preprocessStatus[preprocessIndex]['preprocessName']
    preprocessType = dataset.preprocessStatus[preprocessIndex]['preprocessType']
    sparkSupport = dataset.preprocessStatus[preprocessIndex]['sparkSupport']
    params = dataset.preprocessStatus[preprocessIndex]['preprocessParams']
    taskType = dataset.taskType

    # 控制函数调用
    previousData = getDataFromPreprocessDataset(dataset, previousProcessIndex)
    curData = preprocess.preprocessManage(preprocessType, preprocessName, previousData, params, taskType, master=-1,
                                          pipeline=-1)
    setDataToPreprocessDataset(dataset, preprocessIndex, preprocessName, preprocessType, curData)

    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '已完成'
    dataset.save()
    return '预处理成功'
