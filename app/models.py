import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


# 用户类
class User(db.Document):
    # userId = db.IntField(required=True,unique=True)  #用户编号
    username = db.StringField(required=True, unique=True)  # 用户名称
    password = db.StringField(required=True)  # 用户密码
    roles = db.ListField(required=True, default=['editor'])  # 用户角色
    datetime = db.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 注册时间
    introduction = db.StringField()  # 用户简介
    avatar = db.StringField()  # 用户头像
    name = db.StringField()  # 用户姓名
    status = db.StringField(required=True,default=["Normal"])  # 用户状态


# 板块表
class Section(db.Document):
    # sectionId = db.StringField(required=True, unique=True)  # 板块编号  need change  auto increment
    section_name = db.StringField(required=True, unique=True)  # 板块名称
    section_master_name = db.StringField(required=True)  # 版主名称
    section_info = db.StringField(required=True)  # 板块简介
    topic_count = db.IntField(required=True, default=0)  # 板块内主题数量
    # sectionClickCount=db.IntField(required=True, default=0) #板块点击次数


# # 论坛帖子表
# class Post(db.Document):
#     post_id = db.StringField(required=True, unique=True)  # 帖子编号 need change  auto increment
#     section_name = db.StringField(required=True)  # 板块编号
#     post_topic = db.StringField(required=True)  # 帖子主题
#     user_name = db.StringField(required=True)  # 发帖人名称
#     post_content = db.StringField(required=True)  # 帖子内容
#     post_first_time = db.DateTimeField(required=True,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 发帖时间
#     post_last_time = db.DateTimeField(required=True)  # 最后回帖时间
#     post_status = db.StringField(required=True)  # 帖子状态，精华，锁住等
#     reply_count = db.IntField(required=True, default=0)  # 回复数量
#     # postClickCount=db.IntField(required=True,default=0) #帖子点击次数

# 论坛帖子表
class Blog(db.Document):
    blog_id = db.LongField(required=True, unique=True)  # 帖子编号
    title = db.StringField(required=True)  # 帖子主题
    username = db.StringField(required=True)  # 发帖人名称
    content = db.StringField(required=True)  # 帖子内容
    created = db.DateTimeField(required=True, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 发帖时间
    description = db.StringField(required=True)


# 帖子回复表
class Reply(db.Document):
    reply_id = db.StringField(required=True, unique=True)  # 帖子回复ID
    post_id = db.StringField(required=True)  # 帖子ID
    section_id = db.StringField(required=True)  # 板块ID
    user_name = db.StringField(required=True)  # 回复人名称
    reply_content = db.StringField(required=True)  # 回复内容
    reply_time = db.DateTimeField(required=True, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 回复时间


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


# 原始数据集
class OriginalDataset(Dataset):
    originFile = db.StringField(required=True)
    originFileSize = db.StringField()
    text = db.ListField()
    status = db.StringField(required=True)
