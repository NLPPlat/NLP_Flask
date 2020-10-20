from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from concurrent.futures import ThreadPoolExecutor
import json

from . import api
from manage import celery
from app import models, files
from app.utils import file_utils
from app.models.dataset import *
from app.models.venation import *


# 训练数据集文件上传
@api.route('/data/train/file', methods=['POST'])
@jwt_required
def trainFileUpload():
    uploadFile = request.files['file']
    params = request.form
    filename = files.save(uploadFile)
    fileurl = files.path(filename)
    trainFile = OriginalDataset(username=get_jwt_identity(), taskType=params.get('taskType'),
                                taskName=params.get('taskName'), datasetType='原始数据集',
                                desc=params.get('desc'), publicity=params.get('publicity'), originalFile=fileurl,
                                analyseStatus='解析中', annotationStatus='未开始')
    trainFile.save()
    datasetid = int(trainFile.id)
    trainFile.ancestor = datasetid
    trainFile.save()
    originalDatasetNode = DatasetNode(parent=-1, id=datasetid, username=trainFile.username, taskName=trainFile.taskName,
                                      datetime=trainFile.datetime, taskType=trainFile.taskType)
    venation = Venation(ancestor=datasetid)
    venation.originalDataset.append(originalDatasetNode)
    venation.save()
    trainFileUploadAnalyse.delay(fileurl, trainFile)
    return "success"


# 训练数据集文件解析
@celery.task
def trainFileUploadAnalyse(fileurl, trainFile):
    files = file_utils.fileReader(fileurl)
    for text in files:
        textContent = TextContent().from_json(json.dumps(text))
        trainFile.originalData.append(textContent)
    trainFile.analyseStatus = '解析完成'
    trainFile.save()
    return
