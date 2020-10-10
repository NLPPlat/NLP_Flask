from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from concurrent.futures import ThreadPoolExecutor
import json

from . import api
from app import models, files
from app.utils import file
from app.models.dataset import *


# 训练数据集文件上传
@api.route('/data/train/file', methods=['POST'])
@jwt_required
def trainFileUpload():
    uploadFile = request.files['file']
    params = request.form
    filename = files.save(uploadFile)
    fileurl = files.path(filename)
    trainFile = OriginalDataset(username=get_jwt_identity(), taskType=params.get('taskType'),
                                       taskName=params.get('taskName'),
                                       desc=params.get('desc'), publicity=params.get('publicity'), originalFile=fileurl,
                                       analyseStatus='解析中', annotationStatus='未开始')
    trainFile.save()
    executor = ThreadPoolExecutor(1)
    executor.submit(trainFileUploadAnalyse(fileurl, trainFile))
    return "success"


# 训练数据集文件解析
def trainFileUploadAnalyse(fileurl, trainFile):
    with open(fileurl, 'r') as f:
        files = file.csvReader(f)
    for text in files:
        textContent = TextContent().from_json(json.dumps(text))
        trainFile.originalData.append(textContent)
    trainFile.analyseStatus = '解析完成'
    trainFile.save()
    return
