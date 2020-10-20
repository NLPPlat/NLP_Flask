# -*- coding: utf-8 -*-
"""
@Time ： 2020/10/15 13:52
@Auth ： sora
@File ：jieba_util.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import jieba.posseg as posseg
import jieba
from com.sora.utils.pre_process_util import PreProcessUtil


class JiebaUtil(PreProcessUtil):
    def cut(self,text):
        list = []
        seg_list = jieba.cut(text)
        for word in seg_list:
            list.append(word)
        return list

    def postagging(self,text):
        dic_list = []
        seg_list = posseg.cut(text)
        for word, flag in seg_list:
            dic = {
                'word': word,
                'flag': flag
            }
            dic_list.append(dic)
        return dic_list