import csv
import numpy as np
from math import radians, cos, sin, asin, sqrt
from category_distance import CreateLocationCategoryHierarchicalTree, CalCategoryDistance
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

CreateLocationCategoryHierarchicalTree()

venue_num = 0
category_list = []
position_list = []
R = 6371
DMAX = 12

def TraverseVenue():
    global venue_num
    with open('../Dataset/Venues/LA/LA-venues.csv', 'r', encoding='gbk') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        for row in f_csv:
            venue_num += 1
            lat, lon = row[2], row[3]
            item = {'latitude':lat,'longtitude':lon}
            category_list.append(row[len(row)-1])
            position_list.append(item)
    f.close()

def CategoryDistanceMatrix():
    global venue_num
    category_distance_matrix = np.zeros((venue_num, venue_num))
    for i in range(0, venue_num):
        category_distance_matrix[i, i] = 1
        if(category_list[i] != 0 and category_list[i] != -1):
            for j in range(i+1, venue_num):
                if(category_list[j] != 0 and category_list[j] != -1):
                    try:
                        distance = CalCategoryDistance(
                            category_list[i], category_list[j])
                        if(distance < 10):
                            category_distance_matrix[i, j] = 1/(distance+1)
                            category_distance_matrix[j, i] = category_distance_matrix[i, j]
                        else:
                            category_distance_matrix[i, j] = 0
                            category_distance_matrix[j, i] = category_distance_matrix[i, j]
                    except:
                        continue
    np.save("Dataset/Venues/cate_result_LA.npy", category_distance_matrix)

def GeographicalDistanceMatrix():
    global R, DMAX, venue_num
    geographicl_distance_matrix = np.zeros((venue_num, venue_num))
    for i in range(0, venue_num):
        geographicl_distance_matrix[i, i] = 1
        for j in range(i+1, venue_num):
            lat_i, lon_i, lat_j, lon_j = float(position_list[i]['latitude']), float(position_list[i]['longtitude']), float(position_list[j]['latitude']), float(position_list[j]['longtitude'])
            lat_i, lon_i, lat_j, lon_j = map(radians, [lat_i, lon_i, lat_j, lon_j])
            d_lat = lat_i - lat_j
            d_lon = lon_i - lon_j
            geographicl_distance = R * 2 * asin(sqrt(sin(d_lat/2) * sin(d_lat/2) + cos(lat_i) * cos(lat_j) * sin(d_lon/2) * sin(d_lon/2))) 
            if(geographicl_distance <= DMAX):
                geographicl_distance_matrix[i, j] = (DMAX-geographicl_distance)/DMAX
                geographicl_distance_matrix[j, i] = geographicl_distance_matrix[i, j]
            else:
                geographicl_distance_matrix[i, j] = 0
                geographicl_distance_matrix[j, i] = geographicl_distance_matrix[i, j]
    np.save("Dataset/Venues/geo_dis_result_LA.npy", geographicl_distance_matrix)

def LocationCluester():
    cat_matrix = np.load("Dataset/Venues/cate_result_LA.npy")
    geo_matrix = np.load("Dataset/Venues/geo_dis_result_LA.npy")
    sim_matrix = cat_matrix + geo_matrix
    for row in sim_matrix:
        for i in range(0,len(sim_matrix)):
            if(row[i]!=0):
                row[i] = 1/row[i]
            else:
                row[i] = 10                

    db = DBSCAN(eps = 0.9, min_samples = 6, metric='precomputed').fit(sim_matrix)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    raito=len(labels[labels[:] == -1]) / len(labels)            
    print('Estimated number of clusters: %d' % n_clusters_)
    print('Noise raito:',format(raito, '.2%'))

# TraverseVenue()
# CategoryDistanceMatrix()
# GeographicalDistanceMatrix()
LocationCluester()