# -*- coding: utf-8 -*-
"""
@Time ： 2020/10/15 15:53
@Auth ： sora
@File ：common_pre_process_service.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from app.nlp.preprocess.service.pre_process_service import PreProcessService


class CommonPreProcessService(PreProcessService):
    def cut(self, data, type,master=''):
        for data_item in data['vectors']:
            data_item = self.cut_item(data_item=data_item, type=type)
        return data

    def postagging(self, data, type,master=''):
        for data_item in data['vectors']:
            data_item = self.postagging_item(data_item=data_item, type=type)
        return data

    def stopwords(self, data, params, type,master=''):
        for data_item in data['vectors']:
            data_item = self.stopwords_item(data_item=data_item, params=params, type=type)
        return data