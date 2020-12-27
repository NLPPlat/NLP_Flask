# 权限管理工具

from app.models.user import *
from app.utils.response_code import *


# 数据集读权限获取
def datasetReadPermission(dataset, username):
    user = User.objects(username=username).first()
    if dataset:
        if dataset.username == username or 'admin' in user.roles or dataset.publicity == '公开':
            return True
    return False


# 数据集写权限判断
def datasetWritePermission(dataset, username):
    user = User.objects(username=username).first()
    if dataset:
        if dataset.username == username or 'admin' in user.roles:
            return True
    return False


# 无权限返回值
def noPeimissionReturn():
    return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}
