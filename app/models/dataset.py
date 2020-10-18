import datetime
from app import db


# 数据集超类
class Dataset(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True)
    taskType = db.StringField(required=True)
    taskName = db.StringField(required=True)
    datasetType = db.StringField(required=True)
    ancestor = db.IntField()
    desc = db.StringField()
    publicity = db.StringField(required=True)
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    meta = {'allow_inheritance': True}


# 文本向量
class TextContent(db.EmbeddedDocument):
    id = db.IntField()
    group = db.DynamicField()
    label = db.DynamicField(default='')
    title = db.DynamicField()
    text1 = db.DynamicField()
    text2 = db.DynamicField()
    delete = db.StringField()


# 原始数据集
class OriginalDataset(Dataset):
    originalFile = db.StringField(required=True)
    originalFileSize = db.StringField()
    originalData = db.EmbeddedDocumentListField(TextContent)
    analyseStatus = db.StringField(required=True)
    groupOn = db.StringField(default='off')
    annotationStatus = db.StringField(required=True)
    annotationFormat = db.DynamicField()
    annotationPublicity = db.StringField(default='不允许')

#预处理数据集
class PreprocessDataset(Dataset):
    preprocessStatus = db.ListField(default=[{'id':0,'preprocessName':'原始文本','preprocessType':'无','previousProcessID':'无','sparkSupport':False,'preprocessStatus':'已完成'}])
    originalData = db.EmbeddedDocumentListField(TextContent)
    cut = db.EmbeddedDocumentListField(TextContent)
    stopwords = db.EmbeddedDocumentListField(TextContent)
    postagging = db.EmbeddedDocumentListField(TextContent)
    keywords = db.EmbeddedDocumentListField(TextContent)

