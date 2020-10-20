# -*- coding: utf-8 -*-
"""
@Time ： 2020/10/15 14:38
@Auth ： sora
@File ：pre_process_service.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from app.nlp.preprocess.utils.pre_process.jieba_util import JiebaUtil
from abc import abstractmethod

from app.nlp.preprocess.utils.pre_process_util import PreProcessUtil


class PreProcessService:

    util = PreProcessUtil()

    def init(self,params):
        if params['tool'] == 'jieba':
            self.util = JiebaUtil()
        else:
            pass

    def cut_item(self,data_item, type):
        for type_item in type:
            data_item[type_item] = self.util.cut(data_item[type_item])
        return data_item

    def postagging_item(self, data_item, type):
        for type_item in type:
            data_item[type_item] = self.util.postagging(data_item[type_item])
        return data_item

    def stopwords_item(self,data_item, params, type):
        for type_item in type:
            data_item[type_item] = self.util.stopwords(data_item[type_item], params['from'], params['tool'])
        return data_item

    @abstractmethod
    def cut(self,data, type,master):
        pass

    @abstractmethod
    def postagging(self,data, type,master):
        pass

    @abstractmethod
    def stopwords(self,data, params, type,master):
        pass