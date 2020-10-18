import datetime
from app import db


# 数据节点
class DatasetNode(db.EmbeddedDocument):
    parent = db.IntField(default=-1)
    children = db.ListField()
    id=db.IntField()
    username = db.StringField()
    taskName = db.StringField()


# 数据脉络
class Venation(db.Document):
    ancestor = db.IntField()
    originalDataset = db.EmbeddedDocumentListField(DatasetNode)
    preprocessDataset = db.EmbeddedDocumentListField(DatasetNode)
