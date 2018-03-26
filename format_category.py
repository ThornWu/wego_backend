import csv
from treelib import Node, Tree
import pickle

dataset = []

def CalCategoryLevel(id):
    pkl_file = open('Category/Tree.pkl', 'rb')  # 读取Tree.pkl文件
    tree = pickle.load(pkl_file)
    pkl_file.close()
    return tree.level(id)

def FormatCategory():
    with open('Dataset/Venues/LA/LA-venues-dayu5.csv', 'r', encoding='gbk') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        selected_category = 0
        selected_level = 0
        for row in f_csv:
            category_num = int(float(row[11]))
            if(category_num == 0):
                continue
            elif(category_num == 1):
                selected_category = str(row[category_num+11])
            else:
                for number in range(11+1,11+category_num):
                    try:
                        level = CalCategoryLevel(str(row[number]))
                        if(level == 3):
                            selected_category = str(row[number])
                            break
                        elif(level > selected_level):
                            selected_level = level
                            selected_category = str(row[number])
                    except:
                        selected_category = -1
            row.append(selected_category)
            dataset.append(row)
        f.close()

    with open('Dataset/Venues/LA/LA-venues.csv','w',encoding='gbk') as f:
        writer = csv.writer(f)
        headers.append('selected_category')
        writer.writerow(headers)
        for row in dataset:
            writer.writerow(row)
        f.close()

FormatCategory()