from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from app import models



# 训练数据集文件上传
@api.route('/data/train/file', methods=['POST'])
@jwt_required
def upload():
    file = request.files['file']
    params = request.form
    user = models.User.objects(username=get_jwt_identity()).first()
    trainFile = models.OriginalDataset(user=user, taskType=params.get('taskType'), name=params.get('name'),
                                     desc=params.get('desc'),publicity=params.get('publicity'))
    trainFile.originFile.put(file)
    trainFile.save()
    return "success"


@api.route('/data/train/file', methods=['GET'])
def download():
    image_first = models.OriginalDataset.objects(description="hello 1").first()
    print(type(image_first.originFile))
    with open('e:/test.txt', 'wb') as f1:
        f1.write(image_first.originFile.read())
    return "ok kang"
