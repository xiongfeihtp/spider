import json
import re
#前面caipi的文件转化为合适的格式
for i in range(11):
    file_name='/Users/xiongfei/PycharmProjects/city_food/label_structure/label_extend/dic_save_dish'+str(i)+'.txt'
    with open(file_name,'r') as f:
        label_all=json.load(f)

    key_list=label_all.keys()
    #'\\u3010\\u6682\\u505c\\u65b0\\u80a1IPO'
    #python3  json  python2 s.decode('unicode-escape')
    dic_save={}
    for label in key_list:
        tmp_list=[]
        for item in label_all[label]:
            food_number=re.search('\d+',item).group()
            tmp_food_name=re.findall(r'"(.+?)"',item)[1]
            #change \\
            try:
                food_name=json.loads('{"foo":"%s"}' % tmp_food_name)
                food_name=food_name['foo']
                tmp_list.append((food_number,food_name))
            except Exception as e:
                tmp_list.append((food_number,tmp_food_name))
        dic_save[label]=tmp_list

    file_name2='/Users/xiongfei/PycharmProjects/city_food/label_structure/label_extend/changed_dic_save_dish'+str(i)+'.txt'
    with open(file_name2,'w') as fp:
        json.dump(dic_save,fp)