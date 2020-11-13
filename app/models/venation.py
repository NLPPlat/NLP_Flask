import datetime
from app import db


# 数据节点
class DatasetNode(db.EmbeddedDocument):
    parent = db.IntField(default=-1)
    children = db.ListField()
    id = db.IntField()
    username = db.StringField()
    taskName = db.StringField()
    taskType = db.StringField()
    datetime = db.DateTimeField()


# 数据脉络
class Venation(db.Document):
    ancestor = db.IntField()
    originalDataset = db.EmbeddedDocumentListField(DatasetNode)
    preprocessDataset = db.EmbeddedDocumentListField(DatasetNode)

# 数据节点
class VenationNode(db.Document):
    id = db.SequenceField(primary_key=True)
    nodeid = db.IntField()
    type = db.StringField()
    parant = db.ListField(defalut=[])
    children = db.ListField(default=[])
