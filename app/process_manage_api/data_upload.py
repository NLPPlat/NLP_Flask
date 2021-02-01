from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery, app
from app.utils.file_utils import *
from app.utils.vector_uitls import *
from app.utils.task_utils import *
from app.utils.venation_utils import *
from app.utils.time_utils import *
from app.utils.response_code import *


# 训练数据集文件上传
@api.route('/data-upload/train-file', methods=['POST'])
@jwt_required
def trainFileUpload():
    # 读取基本数据
    originalFile = request.files['file']
    info = request.values
    username = get_jwt_identity()
    # 存储文件
    filename = originalFile.filename
    fileurl = getFileURL(filename, app)
    originalFile.save(fileurl)
    # 存入Dataset数据库
    originalDataset = OriginalDataset(username=username, taskType=info.get('taskType'),
                                      taskName=info.get('taskName'), datasetType='训练数据集',
                                      desc=info.get('desc'), publicity=info.get('publicity'), originalFile=fileurl,
                                      analyseStatus='解析中', annotationStatus='未开始', datetime=getTime())
    originalDataset.save()
    # 创建节点和任务
    createNode([], '训练数据集', originalDataset.id)
    taskID = createTask('数据接入-' + originalDataset.taskName, '数据接入', originalDataset.id, originalDataset.taskName,
                        username)
    # 解析文件异步任务
    trainFileUploadAnalyse.delay(fileurl, originalDataset, taskID)
    return {'code': RET.OK}


# 训练数据集文件解析异步任务
@celery.task
def trainFileUploadAnalyse(fileurl, originalDataset, taskID):
    # 读取文件
    datasetID = originalDataset.id
    vectors = fileReader(fileurl)
    groupOn = False
    for vector in vectors:
        vector['datasetid'] = datasetID
        if 'group' in vector:
            vector['group'] = int(vector['group'])
            groupOn = True
    vectors_insert(vectors)
    if groupOn:
        originalDataset.groupOn = 'on'
    # 已就绪，状态写入
    originalDataset.analyseStatus = '已就绪'
    originalDataset.save()
    completeTask(taskID)
    return '已就绪'


# 批处理数据集文件上传
@api.route('/data-upload/batch-file', methods=['POST'])
@jwt_required
def batchFileUpload():
    # 读取基本数据
    batchFile = request.files['file']
    info = request.values
    username = get_jwt_identity()
    # 存储文件
    filename = batchFile.filename
    fileurl = getFileURL(filename, app)
    batchFile.save(fileurl)
    # 存入Dataset数据库
    originalBatchDataset = OriginalBatchDataset(username=username, taskType=info.get('taskType'),
                                                taskName=info.get('taskName'),
                                                datasetType='批处理数据集', desc=info.get('desc'),
                                                publicity=info.get('publicity'),
                                                originalFile=fileurl, analyseStatus='解析中', datetime=getTime())
    originalBatchDataset.save()
    # 创建节点和任务
    createNode([], '批处理数据集', originalBatchDataset.id)
    taskID = createTask('数据接入-' + originalBatchDataset.taskName, '数据接入', originalBatchDataset.id,
                        originalBatchDataset.taskName,
                        username)
    # 解析文件异步任务
    batchFileUploadAnalyse.delay(fileurl, originalBatchDataset, taskID)
    return "success"


# 批处理数据集文件解析异步任务
@celery.task
def batchFileUploadAnalyse(fileurl, originalBatchDataset, taskID):
    # 读取文件
    datasetID = originalBatchDataset.id
    vectors = fileReader(fileurl)
    groupOn = False
    for vector in vectors:
        vector['datasetid'] = datasetID
        if 'group' in vector:
            vector['group'] = int(vector['group'])
            groupOn=True
    vectors_insert(vectors, '批处理数据集')
    if groupOn:
        originalBatchDataset.groupOn = 'on'
    # 已就绪，状态写入
    originalBatchDataset.analyseStatus = '已就绪'
    originalBatchDataset.save()
    completeTask(taskID)
    return '已就绪'
