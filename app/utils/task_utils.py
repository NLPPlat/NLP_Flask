import json
from mongoengine import Q

from app.models.task import *


def createTask(taskName, taskType, datasetID, datasetName, username):
    task = Task(taskName=taskName, taskType=taskType, datasetID=datasetID, datasetName=datasetName, taskStatus='执行中',
                username=username)
    task.save()
    return task.id


def completeTask(taskID):
    task = Task.objects(id=taskID).first()
    task.taskStatus = '已完成'
    task.save()
    return
