# 权限管理工具

from app.models.dataset import *
from app.models.user import *
from app.models.pipeline import *
from app.models.resource import *
from app.utils.response_code import *


# 读权限获取
def readPermission(data, username):
    user = User.objects(username=username).first()
    if data:
        if data.username == username or 'admin' in user.roles or data.publicity == '公开':
            return True
    return False


# 写权限判断
def writePermission(data, username):
    user = User.objects(username=username).first()
    if data:
        if data.username == username or 'admin' in user.roles:
            return True
    return False


# 用户信息写权限判断
def userinfoWritePermission(username, realUsername):
    user = User.objects(username=realUsername).first()
    if username == realUsername or 'admin' in user.roles:
        return True
    return False


# 重名判断
def namePermission(dataName, dataType):
    if dataType == '数据集':
        query = Dataset.objects(taskName=dataName).first()
    elif dataType == '管道文件':
        query = Pipeline.objects(pipelineName=dataName).first()
    if query:
        return False
    else:
        return True


# 无权限返回值
def noPeimissionReturn():
    return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 重名返回值
def repeatNameReturn():
    return {'code': RET.FORBBIDEN, 'message': '已存在相同名称'}
