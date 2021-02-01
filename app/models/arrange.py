from app import db


# 线上部署类
class Arrange(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True)
    taskType = db.StringField(required=True)
    arrangeName = db.StringField(required=True)
    arrangeStatus = db.StringField()
    trainedmodel = db.StringField()
    pipeline = db.StringField()
    publicity = db.StringField(required=True)
    desc = db.StringField()
    url = db.StringField()
    datetime = db.DateTimeField()


# 部署监控类
class ArrangeMonitor(db.DynamicDocument):
    arrange = db.IntField()
    day = db.IntField()
    hour = db.IntField()
    count = db.IntField(default=0)
