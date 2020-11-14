from mongoengine import Q

from app.models.venation import *
from app.models.dataset import *
from app.models.model import *
from app.models.pipeline import *


# 创建脉络节点
def createNode(parents, type, nodeid):
    venationNode = VenationNode(type=type, nodeid=nodeid, parents=parents)
    venationNode.save()
    for parent in parents:
        parentVenation = VenationNode.objects(id=parent).first()
        parentVenation.children.append(venationNode.id)
        parentVenation.save()
    return venationNode.id


# 寻找所有关系
def findALlRelations(type, nodeid):
    venationNode = findNode(type, nodeid)
    venation = {'训练数据集': [], '预处理数据集': [], '特征数据集': [], '批处理数据集': [], '批处理特征集': [], '结果数据集': [], '训练模型对象': [],
                '预处理管道对象': []}
    venationIDs = [venationNode.id]
    parents = venationNode.parents
    children = venationNode.children
    while len(parents) > 0:
        parent = parents.pop(0)
        if parent not in venationIDs:
            venationIDs.append(parent)
            parents = parents + findParents(parent)
    while len(children) > 0:
        child = children.pop(0)
        if child not in venationIDs:
            venationIDs.append(child)
            children = children + findChildren(child)
    for node in venationIDs:
        nodeInfo = findNodeInfo(node)
        venation[nodeInfo['type']].append(nodeInfo)
    return venation


# 查找节点信息
def findNodeInfo(venationNode):
    venationNode = VenationNode.objects(id=venationNode).first()
    type = venationNode.type
    nodeID = venationNode.nodeid
    if type == '训练模型对象':
        model = TrainedModel.objects(id=nodeID).first()
        name = model.modelName
        username=model.username
        datetime = model.datetime
    elif type == '预处理管道对象':
        pipeline = Pipeline.objects(id=nodeID).first()
        name = pipeline.pipelineName
        username=pipeline.username
        datetime = pipeline.datetime
    else:
        dataset = Dataset.objects(id=nodeID).first()
        name = dataset.taskName
        username=dataset.username
        datetime = dataset.datetime
    return {'id': nodeID, 'type': type, 'name': name, 'username':username, 'datetime': datetime}


# 返回节点
def findNode(type, nodeid):
    venationNode = VenationNode.objects(Q(type=type) & Q(nodeid=nodeid)).first()
    return venationNode


# 返回节点id
def findNodeID(type, nodeid):
    venationNode = VenationNode.objects(Q(type=type) & Q(nodeid=nodeid)).first()
    return venationNode.id


# 寻找直系祖先
def findParents(venationNodeID):
    venationNode = VenationNode.objects(id=venationNodeID).first()
    return venationNode.parents


# 寻找直系孩子
def findChildren(venationNodeID):
    venationNode = VenationNode.objects(id=venationNodeID).first()
    return venationNode.children
