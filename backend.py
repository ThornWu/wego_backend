from bottle import route, run, template, request, redirect, response
from math import radians, cos, sin, asin, sqrt
import sqlite3
import os
import json,pickle
import time,random
from processmodel import * 
# import hashlib

SQL_PATH = os.path.join(os.getcwd(),"wego.db")
# SQL_PATH = os.path.join("/usr/tomcat/apache-tomcat-9.0.8/webapps/ROOT/WEB-INF/classes","wego.db")
con = sqlite3.connect(SQL_PATH)

R = 6371 

@route('/register', method='POST')
def do_register():
    # m = hashlib.sha256()
    userid = int(round(time.time() * 1000))
    username = request.forms.get('username')
    password = request.forms.get('password')
    email = request.forms.get('email')
    # m.update(password.encode(encoding='utf-8'))
    gender = True
    data = {}
    if(username!=None and password!=None and email!=None):
        try:
            con.execute('insert into user(userid,username,password,email,gender) values(?,?,?,?,?)',[userid,username,password,email,gender])
            con.commit()
            data = {"text":"Register successful", "code":"OK"}
        except:
            data = {"text":"Please choose another username", "code":"Error"}
    else:
        data = {"text":"Invaild Request","code":"Error"}
    return json.dumps(data)

@route('/login',method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    data = {}
    print(username,password)
    if(username!=None and password!=None):
        try:
            c = con.cursor()
            c.execute("select * from user where username=(?)",[username])
            result = c.fetchall()
            if password == result[0][2]:
                if (result[0][-1]=='True'):
                    data = {"text":"Login successful", "code":"OK", "user":{"userid":result[0][0],"username":result[0][1]}}
                else:
                    data = {"text":"Your account is forbidden", "code":"Error"}
            else:
                data = {"text":"Login failed", "code":"Error"}
        except:
            data = {"text":"Login failed", "code":"Error"}
    else:
        data = {"text":"Invaild Request","code":"Error"}
    return json.dumps(data)

@route('/userhome')
def do_getuserhome():
    currentuser = request.query.currentuser
    targetuser = request.query.targetuser

    data = {}

    if(currentuser!="" and targetuser!=""):
        try:
            c = con.cursor()
            c.execute("select userid,username,gender,homecity from user where userid = (?)",[targetuser])
            basicinfo = c.fetchall()
            c = con.cursor()
            c.execute("select E.categoryname,F.* from category as E join (select C.* ,D.createtime from venue as C join (select venueid,createtime from tip as A join (select * from user where user.userid =(?)) as B on A.userid = B.userid) as D on C.venueid = D.venueid order by D.createtime desc) as F on E.categoryid = F.category limit 10",[targetuser])
            recenthistory = c.fetchall()
            recenthistory_format=[]
            for item in recenthistory:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6],"createtime":item[11]}
                recenthistory_format.append(item_json)
            c = con.cursor()
            c.execute("select count(userb) as uesrbcount from friendship where usera = (?)",[targetuser])
            following = c.fetchall()
            c = con.cursor()
            c.execute("select count(usera) as uesracount from friendship where userb = (?)",[targetuser])
            followers = c.fetchall()
            c = con.cursor()
            c.execute("select * from friendship where usera = (?) and userb = (?)",[currentuser,targetuser])
            isfriend = c.fetchall()
            data = {"userid":basicinfo[0][0],"username":basicinfo[0][1],"gender":"Male" if(basicinfo[0][2]==1) else "Female",
            "city":basicinfo[0][3],"history":recenthistory_format,"following":following[0][0],"followers":followers[0][0],
            "isfriend":"True" if(len(isfriend)!=0) else "False"}
        except:
            print("Error")
    return json.dumps(data)

@route('/friendship')
def do_handlefrienship():
    usera = request.query.usera    
    userb = request.query.userb
    action = request.query.action
    data = {}
    if (usera!="" and userb!="" and usera!=userb):
        try:
            if(action=="add"):
                con.execute('insert into friendship(usera,userb) values(?,?)',[usera,userb])
                con.commit()
                data = {"text":"Add successful", "code":"OK"}
            elif(action=="del"):
                con.execute('delete from friendship where usera=(?) and userb=(?)',[usera,userb])
                con.commit()
                data = {"text":"Delete successful", "code":"OK"}
            else:
                data = {"text":"Invaild Request","code":"Error"}
        except:
            data = {"text":"Operation failed, place try again", "code":"Error"}
    else:
        data = {"text":"Invaild Request","code":"Error"}
    return json.dumps(data)

@route('/friendlist')
def do_getfriendlist():
    userid = request.query.userid
    action = request.query.action
    data = {}
    if (userid!=""):
        try:
            if(action=="following"):
                c = con.cursor()
                c.execute("select userid,username,gender,homecity from user where userid in (select userb from friendship where usera = (?)) limit 100",[userid])
                result = c.fetchall()
                result_format=[]
                for item in result:
                    item_json = {"userid":item[0],"username":item[1],"gender":"Male" if(item[2]==1) else "Female","homecity":item[3]}
                    result_format.append(item_json)
                data = {"text":"OK","code":"OK","result":result_format}
            elif(action=="followers"):
                c = con.cursor()
                c.execute("select userid,username,gender,homecity from user where userid in (select usera from friendship where userb = (?)) limit 100",[userid])
                result = c.fetchall()
                result_format=[]
                for item in result:
                    item_json = {"userid":item[0],"username":item[1],"gender":"Male" if(item[2]==1) else "Female","homecity":item[3]}
                    result_format.append(item_json)
                data = {"text":"OK","code":"OK","result":result_format}
            else:
                data = {"text":"Invaild Request","code":"Error","result":[]}
        except:
            data = {"text":"Operation failed, place try again", "code":"Error","result":[]}        
    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}
    return json.dumps(data)

@route('/searchfriend')
def handle_search_friend():
    keyword = request.query.keyword
    data = {}
    if (keyword!=""):
        try:
            keyword = '%' + keyword + '%'
            c = con.cursor()
            c.execute("select userid,username,gender,homecity from user where username like (?) limit 100",[keyword])
            result = c.fetchall()
            result_format=[]
            for item in result:
                item_json = {"userid":item[0],"username":item[1],"gender":"Male" if(item[2]==1) else "Female","homecity":item[3]}
                result_format.append(item_json)
            data = {"text":"OK", "code":"OK","result":result_format}
        except:
            data = {"text":"Operation failed, place try again", "code":"Error","result":[]}
    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}
    return json.dumps(data)

@route('/positioninfo')
def do_getpositioninfo():
    userid = request.query.userid
    venueid = request.query.venueid
    data = {}
    if(userid!="" and venueid!=""):
        try:
            c = con.cursor()
            c.execute("select A.categoryname,B.* from category as A join (select * from venue where venueid = (?)) as B on A.categoryid = B.category",[venueid])
            result = c.fetchall()
            position = result[0]
            
            c = con.cursor()
            c.execute("select createtime from tip where userid =(?) and venueid = (?) order by createtime desc limit 1",[userid,venueid])
            result = c.fetchall()
            if(len(result)!=0):
                lastvisited = result[0][0]
            else:
                lastvisited = 0

            c = con.cursor()
            c.execute("select * from favorite where userid =(?) and venueid = (?)",[userid,venueid])
            result = c.fetchall()
            isstarred = "True" if(len(result)!=0) else "False"
            data = {"category":position[0],"venueid":position[1],"venuename":position[2],"latitude":position[4],"longitude":position[5],"address":position[6],"isused":position[-1],"lastvisited":lastvisited,"isstarred":isstarred}
        except:
            print("Error")

    return json.dumps(data)

@route('/userinfo')
def handle_userinfo():
    userid = request.query.userid
    key = request.query.key
    value = request.query.value
    data={}
    if(userid!="" and key!="userid" and key!="username" and key!="password" and key!="isused" and key!="la_label" and key!="ny_label"):
        try:
            con.execute("update user set "+key+" = (?)",[value])
            con.commit()
            data = {"text":"Edit successfully","code":"OK"}
        except:
            data = {"text":"Invaild Request","code":"Error"}
    else:
        data = {"text":"Invaild Request","code":"Error"}
    return json.dumps(data)

@route('/sign')
def do_handlesign():
    userid = request.query.userid
    venueid = request.query.venueid
    data = {}
    if(userid!="" and venueid!=""):
        try:
            createtime = time.time()
            con.execute('insert into tip(userid,venueid,createtime) values(?,?,?)',[userid,venueid,createtime])
            con.commit()
            data = {"text":"Sign successful", "code":"OK"}
            return json.dumps(data)
        except:
            data = {"text":"Sign failed, place try again", "code":"Error"}
    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}        
    return json.dumps(data)

@route('/history')
def do_handlehistory():
    userid=request.query.userid
    if(userid!=""):
        try:
            c = con.cursor()
            c.execute("select E.categoryname,F.* from category as E join (select C.* ,D.createtime from venue as C join (select venueid,createtime from tip as A join (select * from user where user.userid =(?)) as B on A.userid = B.userid) as D on C.venueid = D.venueid order by D.createtime desc) as F on E.categoryid = F.category limit 100",[userid])
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6],"createtime":item[11]}
                result_format.append(item_json)
            data = {"text":"OK", "code":"OK","result":result_format}
        except:
            data = {"text":"Operation failed, place try again", "code":"Error","result":[]}
    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}
    return json.dumps(data) 

@route('/favorite')
def do_handlefavorite():
    userid = request.query.userid
    venueid = request.query.venueid
    action = request.query.action
    data = {}
    if(userid!="" and venueid!=""):
        if(action == "add"):
            try:
                createtime = time.time()
                con.execute('insert into favorite(userid,venueid,createtime) values(?,?,?)',[userid,venueid,createtime])
                con.commit()
                data = {"text":"Add successful", "code":"OK","result":[]}
            except:
                data = {"text":"This place has been added in your favorite", "code":"Error","result":[]}
        elif(action == "delete"):
            try:
                con.execute('delete from favorite where userid=(?) and venueid=(?)',[userid,venueid])
                con.commit()
                data = {"text":"Delete successful", "code":"OK","result":[]}
            except:
                data = {"text":"This place has not been added in your favorite", "code":"Error","result":[]}
    elif(userid!=""):
        try:
            c = con.cursor()
            c.execute("select A.categoryname,B.* from category as A join (select * from venue where venueid in (select venueid from favorite where userid=(?))) as B on A.categoryid = B.category",[userid])
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
            data = {"text":"OK", "code":"OK","result":result_format}
        except:
            data = {"text":"Operation failed, place try again", "code":"Error","result":[]}
    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}
    return json.dumps(data)

@route('/search')
def do_search():
    city = request.query.city
    keyword = request.query.keyword
    lat = request.query.lat
    lon = request.query.lon
    DMAX = int(request.query.dmax) if (request.query.dmax!="") else 10

    c = con.cursor()
    result = []
    data = {}
    err_flag = 0
    if(keyword!="" and lat!="" and lon!=""):
        if(keyword=="restaurant"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '3' or categoryid='3') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '3' or categoryid='3') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="mall"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d1fd941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d1fd941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="nightlife"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid ='6' or categoryid = '6') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid ='6' or categoryid = '6') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="hotel"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d1f0941735' or categoryid='4bf58dd8d48988d1fa931735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d1f0941735' or categoryid='4bf58dd8d48988d1fa931735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="park"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d182941735', '4bf58dd8d48988d193941735', '4bf58dd8d48988d163941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d182941735', '4bf58dd8d48988d193941735', '4bf58dd8d48988d163941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="movie"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d17f941735' or categoryid='4bf58dd8d48988d17f941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d17f941735' or categoryid='4bf58dd8d48988d17f941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="museum"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d181941735' or categoryid='4bf58dd8d48988d181941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d181941735' or categoryid='4bf58dd8d48988d181941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        elif(keyword=="stadium"):
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d184941735' or categoryid='4bf58dd8d48988d184941735' or parentid ='4bf58dd8d48988d1b4941735' or categoryid='4bf58dd8d48988d1b4941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d184941735' or categoryid='4bf58dd8d48988d184941735' or parentid ='4bf58dd8d48988d1b4941735' or categoryid='4bf58dd8d48988d1b4941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        else:
            try:
                keyword = '%' + keyword + '%'
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where venuename like (?) and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category",[keyword])
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where venuename like (?) and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on D.categoryid = C.category",[keyword])                
                result = c.fetchall()
            except:
                err_flag = 1
        if(err_flag!=1):
            result_format = []
            for item in result:
                lat_i, lon_i, lat_j, lon_j = float(lat), float(lon), float(item[4]), float(item[5])
                lat_i, lon_i, lat_j, lon_j = map(radians, [lat_i, lon_i, lat_j, lon_j])
                d_lat = lat_i - lat_j
                d_lon = lon_i - lon_j
                geographicl_distance = R * 2 * asin(sqrt(sin(d_lat/2) * sin(d_lat/2) + cos(lat_i) * cos(lat_j) * sin(d_lon/2) * sin(d_lon/2))) 
                if(geographicl_distance<=DMAX):
                    item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6],"distance":geographicl_distance}
                    result_format.append(item_json)
                if(len(result_format)>=50):
                    break
            data = {"text":"OK", "code":"OK","result":result_format}
        else:
            data = {"text":"Operation failed, place try again", "code":"Error","result":[]}
    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}
    return json.dumps(data)
    
@route('/recommend')
def do_recommend():
    userid = request.query.userid
    # 0-3: weekday 4-7:weekend 0\4:morning 1\5:afternoon 2\6:evening 3\7:midnight
    timeid = int(request.query.timeid) if(request.query.timeid!="") else 0
    lat = request.query.lat
    lon = request.query.lon
    city = "LA" if(request.query.city=="LA") else "NYC"

    DMAX = 15 
    TOPK = 10
    TOPN = 5

    c = con.cursor()
    result = []
    data = {}
    err_flag = 0
    if(lat!="" and lon!="" and userid!=""):
        try:
            R1 = pickle.load(open(os.path.join(os.getcwd(),'Origin','Model', city + '_' + str(timeid) + '_' + userid + '.pkl'),'rb'))
            top_k_cluster = findTopKCluster(R1,TOPK,int(userid))
            venue_list = []
            for i in range(len(top_k_cluster)):
                pops = cal_popularity(top_k_cluster[i],city)
                venues = findTopKVenue(pops,TOPN,top_k_cluster[i],city)
                for j in range(len(venues)):
                    venue_list.append(venues[j])
            venuetext = ""
            for i in range(len(venue_list)):
                if(i==0):
                    venuetext = venuetext + "'" + venue_list[i] + "'"
                else:
                    venuetext = venuetext + ", " + "'" + venue_list[i] + "'"    
            try:
                c.execute("select D.categoryname,C.* from category as D join(select * from venue where venueid in (" + venuetext + ") ) as C on D.categoryid = C.category")                
                result = c.fetchall()
            except:
                err_flag = 1
        except:
            try:
                if(city=="LA"):
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where la_label!=-2) ) as B on A.venueid = B.venueid) as C on D.categoryid = C.category limit "+ str(int(random.random()*1000)*timeid)+",500")
                else:
                    c.execute("select D.categoryname,C.* from category as D join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where ny_label!=-2) ) as B on A.venueid = B.venueid) as C on D.categoryid = C.category limit "+ str(int(random.random()*1000)*timeid)+",500")                
                result = c.fetchall()
            except:
                err_flag = 1

        if(err_flag!=1):
            result_format = []
            for item in result:
                lat_i, lon_i, lat_j, lon_j = float(lat), float(lon), float(item[4]), float(item[5])
                lat_i, lon_i, lat_j, lon_j = map(radians, [lat_i, lon_i, lat_j, lon_j])
                d_lat = lat_i - lat_j
                d_lon = lon_i - lon_j
                geographicl_distance = R * 2 * asin(sqrt(sin(d_lat/2) * sin(d_lat/2) + cos(lat_i) * cos(lat_j) * sin(d_lon/2) * sin(d_lon/2))) 
                if(geographicl_distance<=DMAX):
                    item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6],"distance":geographicl_distance}
                    result_format.append(item_json)
                if(len(result_format)>=10):
                    break
            data = {"text":"OK", "code":"OK","result":result_format}
        else:
            data = {"text":"Operation failed, place try again", "code":"Error","result":[]}

    else:
        data = {"text":"Invaild Request","code":"Error","result":[]}
    return json.dumps(data)

run(reloader=True, host='0.0.0.0', port=8088)

