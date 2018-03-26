import json
from treelib import Node, Tree
import pickle

# 建立位置类别层次树
# tree.create_node("id", "id", parent="id", data='name')# Node格式
def CreateLocationCategoryHierarchicalTree():
    tree = Tree()
    f = open('categories1.txt','r')
    for line in f:
        result = json.loads(line)
    tree.create_node('root', 'root')# root node
    for i in range(len(result['response']['categories'])):
        top_category = result['response']['categories'][i]
        tree.create_node(top_category['name'], top_category['name'], parent="root", data=top_category['name'])
    #     print(result['response']['categories'][i])# 打印一级分类
        for j in range(len(top_category['categories'])):# 遍历一级分类下的所有类别
            secondry_category = top_category['categories'][j]# 二级分类
    #         print(result['response']['categories'][i]['categories'])
            if secondry_category['categories']:#判断是否有三级分类，如果有将三级分类遍历
    #             print(secondry_category[j])
                tree.create_node(secondry_category['id'], secondry_category['id'],
                                 parent=top_category['name'], data=secondry_category['name'])# 添加二级分类节点，父节点为一级分类节点
    #             print('you-----sanji')
                for k in range(len(secondry_category['categories'])):# 遍历二级分类下的所有类别
                    third_category = secondry_category['categories'][k]
    #                 print(third_category[k])
                    tree.create_node(third_category['id'], third_category['id'],
                                 parent=secondry_category['id'], data=third_category['name'])# 添加三级分类节点，父节点为二级分类节点
            else:# 判断出没有三级分类
    #             print('wu---sanji')
    #             print(secondry_category)# 打印二级分类
                tree.create_node(secondry_category['id'], secondry_category['id'],
                                 parent=top_category['name'], data=secondry_category['name'])# 添加二级分类节点，父节点为一级分类节点
    # print(tree.to_json())# 打印构建好的树
    # print(tree.is_branch('4bf58dd8d48988d17f941735'))
    # print(tree.level('root'))
    # print(tree.level('4bf58dd8d48988d17f941735'))
    output = open('Tree.pkl', 'wb')
    pickle.dump(tree, output)# 将构建好的树存入Tree.pkl文件
    f.close()
    output.close()

# 计算两个位置之间的类别距离

# 写判断两个节点之间类别距离的函数
# 1.首先判断两个节点的类别id是否相等
# 2.如果相等，两者之间的类别距离为0
# 3.如果不等，判断两个节点的tree.level是否相等
# 4.如果两个节点的level相等，判断两个节点的tree.parent是否相等
# 5.如果两个节点的tree.parent相等，则两者之间的类别距离为1，否则两者类别距离为无穷大
# 6.如果两个节点的level不相等，判断两个节点的父节点和另一个节点本身是否相等
# 7.如果相等，则两者之间的类别距离为1，否则两者类别距离为无穷大
def CalCategoryDistance(id1, id2):
    pkl_file = open('Tree.pkl', 'rb')# 读取Tree.pkl文件
    tree = pickle.load(pkl_file)
    dist = 0
    if id1 == id2:# 判断两个节点的类别id是否相等
        dist = 0
        return dist
    else:# 两个节点的类别id不相等
        if tree.level(id1) == tree.level(id2):# 判断两个节点的tree.level是否相等
            if tree.level(id1) == 2:# 如果id1的类别层次为2，它们的parent相等，则距离为1，否则为无穷大
                if tree.parent(id1) == tree.parent(id2):
                    dist = 1
                    return dist
                else:
                    dist = 10
                    return dist
            else:# 如果id1的类别层次为3，它们的parent节点相等，则距离为1
                if tree.parent(id1) == tree.parent(id2):# 两个节点的父节点是否相同
                    dist = 1
                    return dist
                elif tree.parent(tree.parent(id1).tag) == tree.parent(tree.parent(id2).tag):# 两个节点的祖先节点是否相同，相等则距离为2
                    dist = 2
                    return dist
                else:
                    dist = 10
                    return dist
        else:
            if tree.parent(id1) == id2 or id1 == tree.parent(id2):# 判断两个节点的父节点和另一个节点本身是否相等
                dist = 1
                return dist
            if tree.level(id1) < tree.level(id2):# 如果id1是上层节点，判断id1的祖先节点和id2的祖先节点是否相等
                # 这种情况下id1的层次为2，id2的层次为3
                if tree.parent(tree.parent(id1).tag) == tree.parent(tree.parent(tree.parent(id2).tag).tag):
                    dist = 2
                    return dist
                else:
                    dist = 10
                    return dist
            else:# 如果id2是上层节点，判断id1的祖先节点和id2的祖先节点是否相等
                # 这种情况下id1的层次为3，id2的层次为2
                if tree.parent(tree.parent(tree.parent(id1).tag).tag) == tree.parent(tree.parent(id2).tag):
                    dist = 2
                    return dist
                else:
                    dist = 10
                    return dist

    # print(tree.to_json())# 打印构建好的树
    pkl_file.close()

CreateLocationCategoryHierarchicalTree()
id1 = '4bf58dd8d48988d105951735'
id2 = '4bf58dd8d48988d1f0931735'
result = CalCategoryDistance(id1, id2)
print(result)