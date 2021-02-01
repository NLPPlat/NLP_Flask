import datetime
from app import db


# 用户类
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    roles = db.ListField(required=True, default=['editor'])
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    introduction = db.StringField()
    avatar = db.StringField()
    name = db.StringField()
    email = db.StringField()
    phone = db.StringField()
    status = db.StringField()


# 钱包类
class Wallet(db.Document):
    username = db.StringField(required=True)
    money = db.FloatField(default=0.0)


# 订单类
class Order(db.Document):
    username = db.StringField(required=True)
    type = db.StringField()
    salesperson = db.StringField()
