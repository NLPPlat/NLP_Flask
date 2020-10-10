import datetime
from app import db


# 数据集超类
class Dataset(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True)
    taskType = db.StringField(required=True)
    taskName = db.StringField(required=True)
    desc = db.StringField()
    publicity = db.StringField(required=True)
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    meta = {'allow_inheritance': True}


# 文本向量
class TextContent(db.EmbeddedDocument):
    id = db.IntField()
    label = db.DynamicField()
    title = db.StringField()
    text1 = db.StringField()
    text2 = db.StringField()
    delete = db.StringField()


# 原始数据集
class OriginalDataset(Dataset):
    originalFile = db.StringField(required=True)
    originalFileSize = db.StringField()
    originalData = db.EmbeddedDocumentListField(TextContent)
    analyseStatus = db.StringField(required=True)
    annotationStatus = db.StringField(required=True)
    annotationFormat = db.DynamicField()

#预处理数据集
class PreprocessDataset(Dataset):
    preprocessStatus = db.ListField(default=[{'preprocessName':'原始文本','preprocessType':'无','sparkSupport':False,'preprocessStatus':'已完成'}])
    originalData = db.EmbeddedDocumentListField(TextContent)
