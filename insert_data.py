import csv
import sqlite3
import os
import json

PROJECT_ROOT = os.getcwd()
SQL_PATH = os.path.join(os.getcwd(),"wego.db")
con = sqlite3.connect(SQL_PATH)


# 默认一个表中不存在相同 userid 的情况
# 多次操作后 commit
    
def DoInsertUser(dataset):
    count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Users",dataset,dataset+"-users.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            userid = int(item[0])
            username = item[0]
            password = "123456"
            email = "test@thornwu.com"
            gender = (item[4] == "male")
            homecity = (item[5]).split(',')[0]

            try:
                c = con.cursor()
                c.execute("select * from user where userid=(?)", [userid])
                result = c.fetchall()
                if(len(result)==0):
                    try:
                        con.execute('insert into user(userid,username,password,email,gender,homecity) values(?,?,?,?,?,?)',[userid,username,password,email,gender,homecity])
                    except:
                        print("Some errors happened when inserting data to the dataset. UserId=" + str(userid) )
            except:
                print("Some errors happened when selecting data from the dataset")
            
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()
    print("Finish insert user datas in " + dataset)

def DoInsertVenue(dataset):
    count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Venues",dataset,dataset+"-venues.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            venueid = item[0]
            venuename = item[1]
            category = item[-1]
            latitude = float(item[2])
            longitude = float(item[3])
            address = item[4]
            localcity = item[5]

            # if(category == "-1"):
            #     continue

            try:
                c = con.cursor()
                c.execute("select * from venue where venueid=(?)", [venueid])
                result = c.fetchall()
                if(len(result)==0):
                    try:
                        con.execute('insert into venue(venueid,venuename,category,latitude,longitude,address,localcity) values(?,?,?,?,?,?,?)',[venueid,venuename,category,latitude,longitude,address,localcity])
                    except:
                        print("Some errors happened when inserting data to the dataset. VenueId=" + str(venueid) )
            except:
                print("Some errors happened when selecting data from the dataset")
            
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()
    print("Finish insert venue datas in " + dataset)
    

def DoInsertTip(dataset):
    count = 0
    error_count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Tips",dataset,dataset+"-tips-dayu10-dayu5.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            userid = int(item[0])
            venueid = item[1]
            createtime = int(item[3])
            try:
                con.execute('insert into tip(userid,venueid,createtime) values(?,?,?)',[userid,venueid,createtime])
            except:
                print("Some errors happened when inserting data to the dataset. UserId=" + str(userid) + ", VenueId=" + venueid + ", Createtime=" + str(createtime))
                error_count = error_count +1
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()
    print("Error count:" + str(error_count))
    print("Finish insert tip datas in " + dataset)


def DoInsertFriendship(dataset):
    count = 0
    error_count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Friendship",dataset,dataset+"-Friendship.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        for item in f_csv:
            usera = int(item[0])
            userb = int(item[1])
            try:
                con.execute('insert into friendship(usera,userb) values(?,?)',[usera,userb])
            except:
                print("Some errors happened when inserting data to the dataset. UserA=" + str(usera) + ", UserB=" + str(userb))
                error_count = error_count +1
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()
    print("Error count:" + str(error_count))
    print("Finish insert friendship datas in " + dataset)

def DoInsertCategory():
    count = 0
    f = open(os.path.join(PROJECT_ROOT,"Origin","Category","categories1.txt"), 'r')
    content = f.read()
    result = json.loads(content)
    categories = result["response"]["categories"]
    print(categories)

    first_count = 1
    for frist in categories:
        try:
            con.execute('insert into category(categoryid,categoryname,parentid) values(?,?,?)',[str(first_count),frist["name"],"0"])
        except:
            print("Some errors happened when inserting data to the dataset. Categoryname=" + frist["name"])
        
        for second in frist["categories"]:
            try:
                con.execute('insert into category(categoryid,categoryname,parentid) values(?,?,?)',[second["id"],second["name"],str(first_count)])
            except:
                print("Some errors happened when inserting data to the dataset. Categoryname=" + second["name"])

            for third in second["categories"]:
                try:
                    con.execute('insert into category(categoryid,categoryname,parentid) values(?,?,?)',[third["id"],third["name"],second["id"]])
                except:
                    print("Some errors happened when inserting data to the dataset. Categoryname=" + third["name"])
        con.commit()    
        first_count = first_count + 1
    f.close()
    print("Finish insert category datas")

def DoUpdateLabel():
    count = 0
    error_count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Result","location_cluster_la.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            venueid = item[0]
            la_label = item[1]
            try:
                con.execute('update venue set la_label = (?) where venueid=(?)',[la_label,venueid])
            except:
                print("Some errors happened when inserting data to the dataset. Venueid=" + venueid + ", LA_label=" + la_label)
                error_count = error_count +1
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()

    count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Result","location_cluster_nyc.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            venueid = item[0]
            ny_label = item[1]
            try:
                con.execute('update venue set ny_label = (?) where venueid=(?)',[ny_label,venueid])
            except:
                print("Some errors happened when inserting data to the dataset. Venueid=" + venueid + ", NYC_label=" + ny_label)
                error_count = error_count +1
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()

    count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Result","user_cluster_LA_min.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            userid = item[0]
            la_label = item[1]
            try:
                con.execute('update user set la_label = (?) where userid=(?)',[la_label,userid])
            except:
                print("Some errors happened when inserting data to the dataset. Userid=" + userid + ", LA_label=" + la_label)
                error_count = error_count +1
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()

    count = 0
    with open(os.path.join(PROJECT_ROOT,"Origin","Result","user_cluster_NYC_min.csv"), 'r', encoding='ISO-8859-1') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # 取出表头
        for item in f_csv:
            userid = item[0]
            ny_label = item[1]
            try:
                con.execute('update user set ny_label = (?) where userid=(?)',[ny_label,userid])
            except:
                print("Some errors happened when inserting data to the dataset. Userid=" + userid + ", NYC_label=" + ny_label)
                error_count = error_count +1
            count = count + 1
            if(count % 3000 == 0):
                con.commit()
                print(count)
        con.commit()
    f.close()
    print("Error count:" + str(error_count))
    print("Finish update labels")

def DoInitAdmin():
    username = "admin"
    password = "admin123456"
    try:
        con.execute('insert into admin(username,password) values(?,?)',[username,password])
        con.commit()
    except:
        print("Some errors happened when init admin")
    print("Finish init admin")

    
DoInsertUser("LA")
DoInsertUser("NYC")
DoInsertVenue("LA")
DoInsertVenue("NYC")
DoInsertTip("LA")
DoInsertTip("NYC")
DoInsertFriendship("LA")
DoInsertFriendship("NYC")
DoInsertCategory()
DoUpdateLabel()
DoInitAdmin()