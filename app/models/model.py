import datetime
from app import db


# 模型
class BaseModel(db.Document):
    id = db.SequenceField(primary_key=True)
    modelName = db.StringField()
    modelType = db.StringField()
    username = db.StringField()
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    publicity = db.StringField()
    desc = db.StringField()
    code = db.StringField()
    platType = db.StringField()


# 训练的模型
class TrainedModel(db.Document):
    id = db.SequenceField(primary_key=True)
    username = db.StringField()
    baseModelID = db.IntField()
    baseDatasetID = db.IntField()
    modelName = db.StringField()
    modelParams = db.DictField(default={})
    publicity = db.StringField(default='不公开')
    datetime = db.DateTimeField()
    endtime = db.DateTimeField()
    desc = db.StringField()
    code = db.StringField()
    platType = db.StringField()
    model = db.StringField()
    type = db.StringField()
    trainStatus = db.StringField(default='未开始')
    result = db.StringField()
    figs = db.DictField(default={})
    evaluation = db.DictField(default={'accuracy': 0, 'precision': 0, 'recall': 0, 'f1': 0})
