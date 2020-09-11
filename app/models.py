import datetime

from . import db


# 用户类
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    roles = db.ListField(required=True, default=['editor'])
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    introduction = db.StringField()
    avatar = db.StringField()
    name = db.StringField()


# 数据集类
class Dataset(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    user = db.ReferenceField(User, required=True, reverse_delete_rule='CASCADE')
    taskType = db.StringField(required=True)
    taskName = db.StringField(required=True)
    desc = db.StringField()
    publicity = db.StringField(required=True)
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    meta = {'allow_inheritance': True}


# 原始数据集
class OriginalDataset(Dataset):
    originFile = db.FileField(required=True)
    originFileSize = db.StringField()
    label = db.ListField()
    title = db.StringField()
    text1 = db.ListField()
    text2 = db.ListField()
