import datetime
from app import db


# 预处理管道对象
class PipelineObject(db.EmbeddedDocument):
    id = db.IntField()
    preprocessName = db.StringField()
    preprocessType = db.StringField()
    preprocessParams = db.DynamicField()
    sparkSupport = db.BooleanField()
    pipeline = db.DynamicField(default=-1)


# 管道类
class Pipeline(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True)
    taskType = db.StringField(required=True)
    pipelineName = db.StringField(required=True)
    publicity = db.StringField(required=True)
    pipelines = db.EmbeddedDocumentListField(PipelineObject)
    datetime = db.DateTimeField()
