import json
from mongoengine import Q

from app.models.dataset import *


# 某个数据集全部向量插入
def vectors_insert(vectors, datasetType='原始数据集'):
    if datasetType == '原始数据集':
        for vector in vectors:
            if '_cls' in vector:
                vector.pop('_cls')
            if '_id' in vector:
                vector.pop('_id')
            vectorSave = OriginalVector.from_json(json.dumps(vector))
            vectorSave.save()
    elif datasetType == '预处理数据集':
        for vector in vectors:
            if '_cls' in vector:
                vector.pop('_cls')
            if '_id' in vector:
                vector.pop('_id')
            vectorSave = PreprocessVector.from_json(json.dumps(vector))
            vectorSave.save()
    return


# 某个数据集按条件查询
def vectors_select(datasetid, options):
    q = Q(datasetid=datasetid)
    if 'label' in options:
        q = q & Q(label=options['label'])
    if 'group' in options:
        q = q & Q(group=options['group'])
    if 'deleted' in options:
        q = q & Q(deleted=options['deleted'])
    vectors = Vector.objects(q)
    return vectors.count(), vectors


# 某个数据集单个向量查询
def vectors_select_one(datasetid, vectorid):
    vector = Vector.objects(Q(datasetid=datasetid) & Q(vectorid=vectorid)).first()
    return vector


# 某个原始数据集批量向量获取(分页功能)
def vectors_select_divide_original(datasetid, deleted, limit, page):
    front = limit * (page - 1)
    end = limit * page
    vectors = OriginalVector.objects(Q(datasetid=datasetid) & Q(deleted=deleted))
    return vectors.count(), vectors[front:end]


# 某个预处理数据集批量向量获取(分页功能)
def vectors_select_divide_preprocess(datasetid, preprocessid, limit, page):
    front = limit * (page - 1)
    end = limit * page
    vectors = PreprocessVector.objects(Q(datasetid=datasetid) & Q(preprocessid=preprocessid))
    return vectors.count(), vectors[front:end]


# 某个原始数据集全部向量获取
def vectors_select_all_original(datasetid):
    vectors = Vector.objects(datasetid=datasetid)
    return vectors

# 某个预处理数据集全部向量获取
def vectors_select_all_preprocess(datasetid,preprocessid):
    vectors = Vector.objects(Q(datasetid=datasetid) & Q(preprocessid=preprocessid))
    return vectors


# 某个数据集全部向量删除
def vectors_delete_all(datasetid):
    Vector.objects(datasetid=datasetid).delete()
    return


# 某个数据集单个向量更新
def vector_update(datasetid, vectorid, vector):
    if '_cls' in vector:
        vector.pop('_cls')
    if '_id' in vector:
        vector.pop('_id')
    vectorQuery = Vector.objects(Q(datasetid=datasetid) & Q(vectorid=vectorid))
    vectorQuery.update(**vector)
    return
