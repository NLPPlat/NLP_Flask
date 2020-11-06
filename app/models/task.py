import datetime
from app import db


class Task(db.Document):
    id = db.SequenceField(primary_key=True)
    username = db.StringField()
    datasetID = db.IntField()
    datasetName = db.StringField()
    taskName = db.StringField()
    taskType = db.StringField()
    taskStatus = db.StringField()
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
