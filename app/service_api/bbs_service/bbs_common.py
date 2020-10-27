from flask import jsonify, request
from app.service_api import api
from app import models
from .bbs_admin import get_maxId


# 发表博客
@api.route('/blog/write', methods=['POST'])
def blog_write():
    data = request.json
    blog_id = get_maxId()
    title = data.get('title')
    username = data.get('username')
    content = data.get('content')
    description = data.get('description')
    blog = models.Blog(blog_id=blog_id + 1, title=title, username=username, content=content, description=description)
    blog.save()
    return jsonify({"code": 200, "msg": "post_blog_success"})


# 查看博客
@api.route('/blog', methods=['GET'])
def blog_get():
    data = request.json
    currentPage = data.get('currentPage')
    total = get_maxId() // 5 + 1
    blog_list = list()
    start_id = (currentPage - 1) * 5 + 1
    try:
        for i in range(0, 5):
            blog = models.Blog.objects(blog_id=start_id).first()
            if blog is None:
                break
            blog_list.append(blog)
            start_id += 1
    finally:
        pass
    if len(blog_list) == 0:
        return jsonify({"code": 400, "msg": "blog_empty"})
    return jsonify({"code": 200, "blogs": blog_list, "currentPage": currentPage, "total": total})


# 查看博客详情
@api.route('/blog/details', methods=['GET'])
def bolg_detail():
    data = request.json
    id = data.get('blogId')
    blog = models.Blog.objects(blog_id=id).first()
    if blog:
        content = blog.content
        return jsonify({"code": 200, "content": content})
    else:
        return jsonify({"code": 400, "msg": "blog_not_exist"})


"""
以下代码暂时不需要
"""


# 获取所有模块信息
@api.route('/section', methods=['GET'])
def get_section():
    sections = models.Section.objects()
    section_set = set()
    for section in sections:
        section_set.add(section.section_name)
    section_list = list(section_set)
    return jsonify({"code": 200, "section_set": "section_list", "message": "get_section_success"})
