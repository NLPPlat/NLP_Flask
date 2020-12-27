import datetime
from app import db
from app.utils.time_utils import *


# 向量超类
class Vector(db.DynamicDocument):
    datasetid = db.IntField()
    vectorid = db.IntField()
    group = db.IntField()
    label = db.DynamicField(default='')
    title = db.DynamicField()
    text1 = db.DynamicField()
    text2 = db.DynamicField()
    deleted = db.StringField()
    meta = {'allow_inheritance': True, 'indexes': ['datasetid']}


# 数据集超类
class Dataset(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True)
    taskType = db.StringField(required=True)
    taskName = db.StringField(required=True)
    datasetType = db.StringField(required=True)
    desc = db.StringField()
    publicity = db.StringField(required=True)
    datetime = db.DateTimeField()
    groupOn = db.StringField(default='off')
    analyseStatus = db.StringField()
    meta = {'allow_inheritance': True}


# 原始数据集向量
class OriginalVector(Vector):
    pass


# 训练数据集
class OriginalDataset(Dataset):
    originalFile = db.StringField(required=True)
    originalFileSize = db.StringField()
    annotationStatus = db.StringField(required=True)
    annotationFormat = db.DynamicField()
    annotationPublicity = db.StringField(default='不允许')


# 批处理数据集向量
class OriginalBatchVector(Vector):
    pass


# 批处理数据集
class OriginalBatchDataset(Dataset):
    originalFile = db.StringField(required=True)
    originalFileSize = db.StringField()
    originalData = db.ListField()


# 预处理向量
class PreprocessVector(Vector):
    peprocessid: db.IntField()
    meta = {'indexes': ['preprocessid']}


# 预处理步骤对象
class PreprocessObject(db.EmbeddedDocument):
    id = db.IntField()
    preprocessName = db.StringField()
    preprocessType = db.StringField()
    feature = db.StringField(default='')
    embedding = db.StringField(default='')
    embedding_matrix = db.StringField(default='')
    vectors = db.ListField(default=[])
    label = db.StringField(default='')
    label_id = db.StringField(default='')
    vocabs = db.StringField(default='')


# 预处理数据集
class PreprocessDataset(Dataset):
    preprocessStatus = db.ListField(default=[
        {'id': 0, 'preprocessName': '原始文本', 'preprocessType': '无', 'previousProcessID': '无', 'sparkSupport': False,
         'preprocessStatus': '已完成'}])
    data = db.EmbeddedDocumentListField(PreprocessObject)
    annotationFormat = db.DynamicField()


# 特征数据集向量
class FeaturesVector(Vector):
    pass


# 特征对象
class FeaturesObject(db.EmbeddedDocument):
    feature = db.StringField(default='')
    embedding = db.StringField(default='')
    embedding_matrix = db.StringField(default='')
    vectors = db.ListField(default=[])
    label = db.StringField(default='')
    label_id = db.StringField(default='')
    vocabs = db.StringField(default='')


# 特征数据集
class FeaturesDataset(Dataset):
    trainStatus = db.StringField(default='未开始')
    features = db.EmbeddedDocumentField(FeaturesObject)
    train = db.EmbeddedDocumentField(FeaturesObject)
    test = db.EmbeddedDocumentField(FeaturesObject)
    featuresShape = db.DynamicField()
    trainShape = db.DynamicField(default='自定义')
    testShape = db.DynamicField(default='自定义')
    splitStatus = db.StringField(default='未完成')
    splitStratify = db.StringField(default='None')
    trainRate = db.DynamicField(default=0.8)
    modelStatus = db.StringField(default='未完成')
    model = db.DynamicField(default='')


# 批处理特征集向量
class FeaturesBatchVector(Vector):
    originalText1 = db.StringField()
    originalText2 = db.StringField()
    pass


# 批处理特征对象
class FeaturesBatchObject(db.EmbeddedDocument):
    feature = db.StringField(default='')
    embedding = db.StringField(default='')
    embedding_matrix = db.StringField(default='')
    vectors = db.ListField(default=[])
    label = db.StringField(default='')
    label_id = db.DynamicField(default='')


# 批处理特征集
class FeaturesBatchDataset(Dataset):
    batchStatus = db.StringField(default='未开始')
    begintime = db.DateTimeField()
    endtime = db.DateTimeField()
    resultDataset = db.IntField(default=-1)
    features = db.EmbeddedDocumentField(FeaturesBatchObject)


# 结果数据集向量
class ResultBatchVector(Vector):
    result = db.DynamicField()
    pass


# 结果数据集
class ResultBatchDataset(Dataset):
    vectors = db.ListField(default=[])
