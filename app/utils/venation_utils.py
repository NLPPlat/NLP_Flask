from mongoengine import Q

from app.models.venation import *


# 创建脉络节点
def createNode(parents, type, nodeid):
    venationNode = VenationNode(type=type, nodeid=nodeid, parents=parents)
    venationNode.save()
    for parent in parents:
        parentVenation = VenationNode.objects(id=parent).first()
        parentVenation.children.append(venationNode.id)
        parentVenation.save()
    return


# 返回节点id
def findNode(type, nodeid):
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
