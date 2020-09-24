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
    username = db.StringField(required=True)
    taskType = db.StringField(required=True)
    taskName = db.StringField(required=True)
    desc = db.StringField()
    publicity = db.StringField(required=True)
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    meta = {'allow_inheritance': True}


class TextContent(db.EmbeddedDocument):
    label=db.StringField()
    title=db.StringField()
    text1=db.StringField()
    text2=db.StringField()

# 原始数据集
class OriginalDataset(Dataset):
    originFile = db.StringField(required=True)
    originFileSize = db.StringField()
    text = db.EmbeddedDocumentListField(TextContent)
    status = db.StringField(required=True)


