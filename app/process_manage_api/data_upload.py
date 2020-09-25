from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from concurrent.futures import ThreadPoolExecutor
import json

from . import api
from app import models, files
from app.utils import fileReader


# 训练数据集文件上传
@api.route('/data/train/file', methods=['POST'])
@jwt_required
def trainFileUpload():
    uploadFile = request.files['file']
    params = request.form
    filename = files.save(uploadFile)
    fileurl = files.path(filename)
    trainFile = models.OriginalDataset(username=get_jwt_identity(), taskType=params.get('taskType'),
                                       taskName=params.get('taskName'),
                                       desc=params.get('desc'), publicity=params.get('publicity'), originFile=fileurl,status='解析中')
    trainFile.save()
    executor = ThreadPoolExecutor(1)
    executor.submit(trainFileUploadAnalyse(fileurl, trainFile))
    return "success"

#训练数据集文件解析
def trainFileUploadAnalyse(fileurl, trainFile):
    with open(fileurl, 'r') as f:
        files = fileReader.csvReader(f)
    for text in files:
        textContent=models.TextContent().from_json(json.dumps(text))
        trainFile.text.append(textContent)
    trainFile.status='解析完成'
    trainFile.save()
    return
