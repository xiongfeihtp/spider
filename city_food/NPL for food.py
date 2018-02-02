# -*- coding: utf-8 -*-

import jieba
import jieba.posseg as pseg
import jieba.analyse

# -*- coding:utf-8 -*-
import json
import os
path='/Users/xiongfei/Desktop/jason_save'
from gensim.models import word2vec


#cut word and save.txt
list = os.listdir(path) #列出文件夹下所有的目录与文件
comment_list={}
No_load_list=[]
for i in range(0,len(list)):
    file = os.path.join(path,list[i])
    if os.path.isfile(file):
        with open(file, 'r') as fp:
            try:
                x = json.load(fp)
                for item in x.keys():
                    comment_list[item]=x[item]
            except Exception as e:
                print("loading error for {}".format(file))
                No_load_list.append(file)

tmp=comment_list.copy()
for word in tmp.keys():
    if tmp[word]:
        continue
    else:
        del comment_list[word]
keys_save=[]
for item in comment_list.keys():
    keys_save.append(item)
    for line in comment_list[item]:
        line_result=jieba.cut(line)
        with open('cut_result.txt','a') as fp:
            fp.write(" ".join(line_result))
sentences = word2vec.Text8Corpus("cut_result.txt")  # 加载语料
model = word2vec.Word2Vec(sentences, size=200)  # 默认window=5




