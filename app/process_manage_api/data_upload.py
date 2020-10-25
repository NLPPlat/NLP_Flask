from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery, app
from app.models.dataset import *
from app.models.venation import *
from app.utils.file_utils import *


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

    # 解析文件
    trainFileUploadAnalyse.delay(fileurl, originalDataset)
    return "success"


# 训练数据集文件解析
@celery.task
def trainFileUploadAnalyse(fileurl, originalDataset):
    files = fileReader(fileurl)
    for text in files:
        textContent = TextContent().from_json(json.dumps(text))
        originalDataset.originalData.append(textContent)
    originalDataset.analyseStatus = '解析完成'
    originalDataset.save()
    return
