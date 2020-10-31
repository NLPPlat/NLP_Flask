import datetime
from app import db


# 模型
class Model(db.Document):
    id = db.SequenceField(primary_key=True)
    modelName = db.StringField()
    modelType = db.StringField()
    username = db.StringField()
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    publicity = db.StringField()
    desc = db.StringField()
    code = db.StringField()


# 训练的模型
class TrainedModel(db.Document):
    id = db.SequenceField(primary_key=True)
    username = db.StringField()
    baseModelID = db.IntField()
    modelName = db.StringField()
    modelParams = db.DictField(default={})
    code = db.StringField()
    model = db.StringField()
    type = db.StringField()
    result = db.StringField()
    figs=db.DictField(default={})
