# -*- coding: utf-8 -*-
"""
@Time ： 2020/10/15 14:09
@Auth ： sora
@File ：pre_process_controller.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from app.nlp.preprocess.service.pre_process.common_pre_process_service import CommonPreProcessService
from app.nlp.preprocess.service.pre_process.spark_pre_process_service import SparkPreProcessService


from gensim.models import word2vec as wc

def cut(data,params,type):
    pre_process_service = CommonPreProcessService()
    pre_process_service.init(params=params)
    return pre_process_service.cut(data=data,type=type)

def postagging(data,params,type):
    pre_process_service = CommonPreProcessService()
    pre_process_service.init(params=params)
    return pre_process_service.postagging(data=data, type=type)

def stopwords(data,params,type):
    pre_process_service = CommonPreProcessService()
    return pre_process_service.stopwords(data=data, params=params,type=type)

def cut_spark(data,params,type,master):
    pre_process_service = SparkPreProcessService()
    pre_process_service.init(params=params)
    return pre_process_service.cut(data=data, type=type,master=master)

def postagging_spark(data,params,type,master):
    pre_process_service = SparkPreProcessService()
    pre_process_service.init(params=params)
    return pre_process_service.postagging(data=data, type=type,master=master)

def stopwords_spark(data,params,type,master):
    pre_process_service = SparkPreProcessService()
    return pre_process_service.stopwords(data=data, params=params,type=type,master=master)

def Word2vec(data,params,type):
    vectors=[]
    for vector in data:
        vectors.append(vector['text1'])
    model = wc.Word2Vec(vectors, size=10)
    return