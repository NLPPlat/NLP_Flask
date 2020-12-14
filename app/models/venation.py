import datetime
from app import db

# 数据节点
class VenationNode(db.Document):
    id = db.SequenceField(primary_key=True)
    nodeid = db.IntField()
    type = db.StringField()
    parents = db.ListField(defalut=[])
    children = db.ListField(default=[])
