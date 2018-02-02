import pickle
import json
import jieba
import jieba.posseg as pseg
import jieba.analyse
import Levenshtein

pkl_file = open('data.pkl', 'rb')
data = pickle.load(pkl_file)

file = open("res.txt")
label_list=[]
while 1:
    line = file.readline()
    if not line:
        break
    tmp=line.replace('\n','')
    label_list.append(tmp)


# fp=open('label_from.txt','r')
# x = json.load(fp)  # 分隔符
# label_list=[]
# for key in x.keys():
#     for i in x[key]:
#         label_list.append(i)

for item in label_list:
    distance = {}
    for i in data.keys():
        for j in data[i].keys():
            for m in data[i][j]:
                distance[m] = Levenshtein.jaro_winkler(m[::-1], item[::-1])
    print(item,sorted(distance.items(), key=lambda item:item[1],reverse=True))



