# -*- coding: utf-8 -*-

import jieba
import jieba.posseg as pseg
import jieba.analyse

# -*- coding:utf-8 -*-
import json
import Levenshtein

fp=open('label_from.txt','r')
x = json.load(fp)  # 分隔符
label_list=[]
for key in x.keys():
    for i in x[key]:
        label_list.append(i)
dict_save={}

for item in label_list:
    result = list(pseg.cut(item))  ##词性标注，标注句子分词后每个词的词性
    dict_save[item]=result



# seg_list = jieba.cut(str1,cut_all = True)   ##全模式
# result = pseg.cut(str1)                     ##词性标注，标注句子分词后每个词的词性

