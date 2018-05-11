import csv
import sqlite3
import os, ast, math
import json
import numpy as np

PROJECT_ROOT = os.getcwd()

location_groups = []    
dataset_num_venueid_dict = {} # 数据表行数:真实id
venue_cate_dict = {} # 数据表行数:类别
venue_group_dict = {} # 数据表行数:组号
venue_tip_dict = {} # 数据库表行数:签到次数
same_category_dict = {} # 类别:同类别位置个数
total = 0

def init(dataset):
    global location_groups,dataset_num_venueid_dict,venue_cate_dict,venue_group_dict,venue_tip_dict,same_category_dict,total
    with open(os.path.join(PROJECT_ROOT,"Origin","Venues",dataset,dataset+"-venues.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for item in f_csv:
            total = total +1
            venueid = item[0]
            checkin_num = item[7]
            category = item[-1]
            dataset_num_venueid_dict.update({total:venueid})
            venue_cate_dict.update({total:category})
            venue_tip_dict.update({total:checkin_num})
            if(category in same_category_dict):
                same_category_dict[category] = same_category_dict[category] + 1
            else:
                same_category_dict.update({category:1}) 
    f.close()

    with open(os.path.join(PROJECT_ROOT, 'Origin', 'Result','location_cluster_'+ dataset +'.txt'),'r',encoding='ISO-8859-1') as f:
        data = f.readlines()
        for line in data:
            a = line.strip('\n').split(":")
            location_groups.append(ast.literal_eval(a[1]))
    f.close()
    for outer in range(len(location_groups)):
        for inner in range(len(location_groups[outer])):
            # -1 聚类为最后一个
            venue_group_dict.update({location_groups[outer][inner]+1:outer})
                

def cal_popularity(groupid):
    venue_pop_matrix = []
    total_tip = 0    
    for i in range(len(location_groups[groupid])):
        total_tip = total_tip + int(venue_tip_dict[location_groups[groupid][i]])
    for i in range(len(location_groups[groupid])):
        venue_cate = venue_cate_dict[location_groups[groupid][i]]
        same_cate_num = same_category_dict[venue_cate]
        venue_tip = venue_tip_dict[location_groups[groupid][i]]
        # print(groupid,location_groups[groupid][i],venue_cate,same_cate_num,venue_tip,total_tip)

        venue_pop = (int(venue_tip)/total_tip) * math.log(total/same_cate_num)
        venue_pop_matrix.append(venue_pop)
    print(venue_pop_matrix)
    return venue_pop_matrix 

def findTopKCluster(arrayR1,arrayI,top_K):
    top_k_matrix = np.zeros((len(arrayR1), top_K))    
    # format_matrix 为将R中在I中为1的位置置0
    format_matrix = np.ones((len(arrayR1),len(arrayI[0])))
    format_matrix[arrayI > 0] = 0

    for i in range(len(format_matrix)):
        for j in range(len(format_matrix[0])):
            format_matrix[i][j] = arrayR1[i][j] * format_matrix[i][j]

    for i in range(len(top_k_matrix)):
        for j in range(len(top_k_matrix[0])):
            max = 0
            for k in range(len(format_matrix[0])):
                if(format_matrix[i][k]>format_matrix[i][max]):
                    max = k
            format_matrix[i][max] = 0
            top_k_matrix[i][j] = max
    print(top_k_matrix)

def findTopKVenue(pop_matrix,top_K,groupid):
    venue_top_matrix = []
    for i in range(top_K):
        max = 0
        for j in range(len(pop_matrix)):
            if(pop_matrix[j] > pop_matrix[max]):
                max = j
        pop_matrix[max] = 0
        venue_top_matrix.append(dataset_num_venueid_dict[location_groups[groupid][max]])
    print(venue_top_matrix)
    return venue_top_matrix


if __name__ == '__main__':
    init("LA")
    R1 = np.array([[1.9,3,2],[3,2.9,5]])
    I = np.array([[1,0,0],[0,1,0]])
    findTopKCluster(R1,I,2)
    pops = cal_popularity(292) #groupid
    venues = findTopKVenue(pops,2,292)