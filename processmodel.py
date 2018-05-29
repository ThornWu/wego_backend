import csv
import sqlite3
import os, ast, math
import json
import numpy as np
import pickle
import time

PROJECT_ROOT = os.getcwd()

location_groups_la = []    
location_groups_nyc = []    
dataset_num_venueid_dict_la = {} # 数据表行数:真实id
dataset_num_venueid_dict_nyc = {} 
venue_cate_dict_la = {} # 数据表行数:类别
venue_cate_dict_nyc = {} 
venue_group_dict_la = {} # 数据表行数:组号
venue_group_dict_nyc = {} 
venue_tip_dict_la = {} # 数据库表行数:签到次数
venue_tip_dict_nyc = {} 
same_category_dict_la = {} # 类别:同类别位置个数
same_category_dict_nyc = {} 
total_la = 0
total_nyc = 0

def init():
    global location_groups_la,dataset_num_venueid_dict_la,venue_cate_dict_la,venue_group_dict_la,venue_tip_dict_la,same_category_dict_la_la,total_la, location_groups_nyc,dataset_num_venueid_dict_nyc,venue_cate_dict_nyc,venue_group_dict_nyc,venue_tip_dict_nyc,same_category_dict_nyc_nyc,total_nyc
    with open(os.path.join(PROJECT_ROOT,"Origin","Venues","LA","LA-venues.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for item in f_csv:
            total_la = total_la +1
            venueid = item[0]
            checkin_num = item[7]
            category = item[-1]
            dataset_num_venueid_dict_la.update({total_la:venueid})
            venue_cate_dict_la.update({total_la:category})
            venue_tip_dict_la.update({total_la:checkin_num})
            if(category in same_category_dict_la):
                same_category_dict_la[category] = same_category_dict_la[category] + 1
            else:
                same_category_dict_la.update({category:1}) 
    f.close()

    with open(os.path.join(PROJECT_ROOT,"Origin","Venues","NYC","NYC-venues.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for item in f_csv:
            total_nyc = total_nyc +1
            venueid = item[0]
            checkin_num = item[7]
            category = item[-1]
            dataset_num_venueid_dict_nyc.update({total_nyc:venueid})
            venue_cate_dict_nyc.update({total_nyc:category})
            venue_tip_dict_nyc.update({total_nyc:checkin_num})
            if(category in same_category_dict_nyc):
                same_category_dict_nyc[category] = same_category_dict_nyc[category] + 1
            else:
                same_category_dict_nyc.update({category:1}) 
    f.close()

    with open(os.path.join(PROJECT_ROOT, 'Origin', 'Result','location_cluster_LA.txt'),'r',encoding='ISO-8859-1') as f:
        data = f.readlines()
        for line in data:
            a = line.strip('\n').split(":")
            location_groups_la.append(ast.literal_eval(a[1]))
    f.close()
    for outer in range(len(location_groups_la)):
        for inner in range(len(location_groups_la[outer])):
            # -1 聚类为最后一个
            venue_group_dict_la.update({location_groups_la[outer][inner]+1:outer})
    
    with open(os.path.join(PROJECT_ROOT, 'Origin', 'Result','location_cluster_NYC.txt'),'r',encoding='ISO-8859-1') as f:
        data = f.readlines()
        for line in data:
            a = line.strip('\n').split(":")
            location_groups_nyc.append(ast.literal_eval(a[1]))
    f.close()
    for outer in range(len(location_groups_nyc)):
        for inner in range(len(location_groups_nyc[outer])):
            # -1 聚类为最后一个
            venue_group_dict_nyc.update({location_groups_nyc[outer][inner]+1:outer})
    print("Init OK")

def cal_popularity(groupid,city):
    venue_pop_matrix = []
    if(city=="LA"):
        total_la_tip = 0
        for i in range(len(location_groups_la[groupid])):
            total_la_tip = total_la_tip + int(venue_tip_dict_la[location_groups_la[groupid][i]])
        for i in range(len(location_groups_la[groupid])):
            venue_cate = venue_cate_dict_la[location_groups_la[groupid][i]]
            same_cate_num = same_category_dict_la[venue_cate]
            venue_tip = venue_tip_dict_la[location_groups_la[groupid][i]]
            # print(groupid,location_groups_la[groupid][i],venue_cate,same_cate_num,venue_tip,total_la_tip)

            venue_pop = (int(venue_tip)/total_la_tip) * math.log(total_la/same_cate_num)
            venue_pop_matrix.append(venue_pop)
    else:
        total_nyc_tip = 0    
        for i in range(len(location_groups_nyc[groupid])):
            total_nyc_tip = total_nyc_tip + int(venue_tip_dict_nyc[location_groups_nyc[groupid][i]])
        for i in range(len(location_groups_nyc[groupid])):
            venue_cate = venue_cate_dict_nyc[location_groups_nyc[groupid][i]]
            same_cate_num = same_category_dict_nyc[venue_cate]
            venue_tip = venue_tip_dict_nyc[location_groups_nyc[groupid][i]]
            # print(groupid,location_groups_nyc[groupid][i],venue_cate,same_cate_num,venue_tip,total_nyc_tip)

            venue_pop = (int(venue_tip)/total_nyc_tip) * math.log(total_nyc/same_cate_num)
            venue_pop_matrix.append(venue_pop)
    return venue_pop_matrix 

def findTopKCluster(arrayR1,top_K,userid):
    top_k_cluster = []  
    for i in range(top_K):
        max = 0
        for j in range(len(arrayR1[0])):
            if(arrayR1[userid][j]>arrayR1[userid][max]):
                max = j
        arrayR1[userid][max] = 0        
        top_k_cluster.append(max) 
    return top_k_cluster

def findTopKVenue(pop_matrix,top_N,groupid,city):
    venue_top_matrix = []
    if(city=="LA"):
        position_num = len(location_groups_la[groupid])
        if(position_num<=top_N):
            for j in range(position_num):
                venue_top_matrix.append(dataset_num_venueid_dict_la[location_groups_la[groupid][j]])
        else:
            max = 0
            for j in range(top_N):
                if(pop_matrix[j] > pop_matrix[max]):
                    max = j
                pop_matrix[max] = 0
                venue_top_matrix.append(dataset_num_venueid_dict_la[location_groups_la[groupid][max]])
    else:
        position_num = len(location_groups_nyc[groupid])
        if(position_num<=top_N):
            for j in range(position_num):
                venue_top_matrix.append(dataset_num_venueid_dict_nyc[location_groups_nyc[groupid][j]])
        else:
            max = 0
            for j in range(top_N):
                if(pop_matrix[j] > pop_matrix[max]):
                    max = j
                pop_matrix[max] = 0
                venue_top_matrix.append(dataset_num_venueid_dict_nyc[location_groups_nyc[groupid][max]])
    return venue_top_matrix

init()

if __name__ == '__main__':
    R1 = pickle.load(open(os.path.join(os.getcwd(), 'Origin', 'Model' , 'LA' + '_0_32' + '.pkl'),'rb'))
    top_k_cluster = findTopKCluster(R1,10,32)
    venue_list = []
    for i in range(len(top_k_cluster)):
        pops = cal_popularity(top_k_cluster[i],"LA") #groupid
        venues = findTopKVenue(pops,5,top_k_cluster[i],"LA")
        for j in range(len(venues)):
            venue_list.append(venues[j])
