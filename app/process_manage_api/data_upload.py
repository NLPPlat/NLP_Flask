from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery, app
from app.models.dataset import *
from app.models.venation import *
from app.utils.file_utils import *
from app.utils.vector_uitls import *
from app.utils.task_utils import *


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
                                      taskName=info.get('taskName'), datasetType='原始数据集',
                                      desc=info.get('desc'), publicity=info.get('publicity'), originalFile=fileurl,
                                      analyseStatus='解析中', annotationStatus='未开始')
    if info.get('taskType') == '文本排序学习':
        originalDataset.groupOn = 'on'
    datasetid = int(originalDataset.id)
    originalDataset.ancestor = datasetid
    originalDataset.save()
    # 存入Venation数据库
    originalDatasetNode = DatasetNode(parent=-1, id=datasetid, username=originalDataset.username,
                                      taskName=originalDataset.taskName,
                                      datetime=originalDataset.datetime, taskType=originalDataset.taskType)
    venation = Venation(ancestor=datasetid)
    venation.originalDataset.append(originalDatasetNode)
    venation.save()
    # 创建任务
    taskID = createTask('数据接入-' + originalDataset.taskName, '数据接入', originalDataset.id, originalDataset.taskName,
                        username)
    # 解析文件
    trainFileUploadAnalyse.delay(fileurl, originalDataset, taskID)
    return "success"


# 训练数据集文件解析
@celery.task
def trainFileUploadAnalyse(fileurl, originalDataset, taskID):
    datasetID = originalDataset.id
    vectors = fileReader(fileurl)
    for vector in vectors:
        vector['datasetid'] = datasetID
        if 'group' in vector:
            vector['group'] = int(vector['group'])
    vectors_insert(vectors)
    originalDataset.analyseStatus = '解析完成'
    originalDataset.save()
    completeTask(taskID)
    return '解析完成'


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
    originalBatchDataset = OriginalBatchDataset(username=username, taskType=info.get('taskType'), taskName=info.get('taskName'),
                                datasetType='批处理数据集', desc=info.get('desc'), publicity=info.get('publicity'),
                                originalFile=fileurl, analyseStatus='解析中')
    if info.get('taskType') == '文本排序学习':
        originalBatchDataset.groupOn = 'on'
    originalBatchDataset.save()
    # 创建任务
    taskID = createTask('数据接入-' + originalBatchDataset.taskName, '数据接入', originalBatchDataset.id, originalBatchDataset.taskName,
                        username)
    # 解析文件
    batchFileUploadAnalyse.delay(fileurl, originalBatchDataset, taskID)
    return "success"


# 训练数据集文件解析
@celery.task
def batchFileUploadAnalyse(fileurl, originalBatchDataset, taskID):
    datasetID = originalBatchDataset.id
    vectors = fileReader(fileurl)
    for vector in vectors:
        vector['datasetid'] = datasetID
        if 'group' in vector:
            vector['group'] = int(vector['group'])
    vectors_insert(vectors,'批处理数据集')
    originalBatchDataset.analyseStatus = '解析完成'
    originalBatchDataset.save()
    completeTask(taskID)
    return '解析完成'
