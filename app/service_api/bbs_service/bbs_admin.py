from flask import jsonify, request
# from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt, get_jwt_identity
from app.service_api import api
from app import models


"""
本文件内代码暂时不需要
"""


# 添加模块信息
@api.route('/section', methods=["POST"])
def add_section():
    g_section = request.json
    section_name = g_section.get("section_name")
    f_section = models.Section.objects(section_name=section_name)
    if not f_section:
        section_master_name = g_section.get("section_master_name")
        section_info = g_section.get("section_info")
        section = models.Section(section_name=section_name, section_master_name=section_master_name,
                                 section_info=section_info)
        section.save()
        return jsonify({"code": 200, "message": "add_section_success"})
    else:
        return jsonify({"code": 400, "message": "section_already_exists"})





# 修改模块信息
@api.route('edit_section', methods=['POST'])
def edit_section():
    section = request.json
    section_name = section.get("section_name")
    new_section = models.Section.objects(section_name=section_name).first()
    if new_section:
        new_section_name = section.get("new_section_name")
        new_section_master_name = section.get("new_section_master_name")
        new_section_info = section.get("new_section_info")
        new_section.update(section_name=new_section_name, section_master_name=new_section_master_name,
                           section_info=new_section_info)
        return jsonify({"code": "200", "message": "edit_section_success"})
    else:
        return jsonify({"code": "400", "message": "section_not_exist"})


# 获取最大帖子ID，尚未学习MongoEngine某列如何自增。。。。
# @api.route('/test',methods=['GET'])
def get_maxId():
    blogs = models.Blog.objects
    blog_id_set = set()
    for blog in blogs:
        blog_id_set.add(blog.blog_id)
        # print(blog.blog_id)
    return max(blog_id_set)