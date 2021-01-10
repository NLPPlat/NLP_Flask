# -*- coding: utf-8 -*-
"""
@Time ： 2020/10/15 14:57
@Auth ： sora
@File ：pre_process_util.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

from abc import ABCMeta,abstractmethod,abstractproperty

from app.models.resource import *

class PreProcessUtil():
    @abstractmethod
    def cut(self,text):
        pass

    @abstractmethod
    def postagging(self,text):
        pass

    def stopwords(self,list,list_type,stopwords):
        # 输出结果为outstr
        out_list = []
        # 去停用词
        for item in list:
            word = item if list_type == '分词' else item['word']
            if word not in stopwords:
                if word != '\t' and word.strip() !='':
                    out_list.append(item)
        return out_list

def stopwordsListReader(stopwordsFileName):
    stopwordsFile = Resource.objects(resourceName=stopwordsFileName).first()
    stopwordsList = [line.strip() for line in open(stopwordsFile.url, encoding='UTF-8').readlines()]
    return stopwordsList