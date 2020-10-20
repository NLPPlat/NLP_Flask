import datetime
from app import db

# 算子
class Operator(db.Document):
    id = db.SequenceField(primary_key=True)
    operatorName=db.StringField()
    operatorType=db.StringField()
    username=db.StringField()
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    publicity=db.StringField()
    desc=db.StringField()
    code=db.StringField()