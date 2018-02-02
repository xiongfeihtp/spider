#
# def levenshtein_distance(first, second):
#     '''
#     计算两个字符串之间的L氏编辑距离
#     :输入参数 first: 第一个字符串
#     :输入参数 second: 第二个字符串
#     :返回值: L氏编辑距离
#     '''
#     if len(first) == 0 or len(second) == 0:
#         return len(first) + len(second)
#     first_length = len(first) + 1
#     second_length = len(second) + 1
#     #python3和python2的区别
#     distance_matrix = [list(range(second_length)) for i in range(first_length)] # 初始化矩阵
#
#     for i in range(1, first_length):
#         for j in range(1, second_length):
#             deletion = distance_matrix[i-1][j] + 1
#             insertion = distance_matrix[i][j-1] + 1
#             substitution = distance_matrix[i-1][j-1]
#             if first[i-1] != second[j-1]:
#                 substitution += 1
#             distance_matrix[i][j] = min(insertion, deletion, substitution)
#     return distance_matrix[first_length-1][second_length-1]


# -*- coding:utf-8 -*-
import json
import Levenshtein

fp=open('label_from.txt','r')
x = json.load(fp)  # 分隔符
label_list=[]
for key in x.keys():
    for i in x[key]:
        label_list.append(i)
while 1:
    s=input("请输入：")
    distance={}
    for i in label_list:
        distance[i]=Levenshtein.jaro_winkler(i[::-1],s[::-1])
        #items()方法将字典转化为元组，key指定一个可迭代的元素
    print(sorted(distance.items(), key=lambda item:item[1],reverse=True))
