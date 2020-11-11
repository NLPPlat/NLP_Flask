import datetime
from app import db

# 资源类
class Resource(db.DynamicDocument):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True)
    resourceName = db.StringField(required=True)
    resourceType = db.StringField(required=True)
    url=db.StringField(required=True)
    desc = db.StringField()
    publicity = db.StringField(required=True)
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))