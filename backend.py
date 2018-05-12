from bottle import route, run, template, request, redirect, response
import sqlite3
import os
import json
import time
# import hashlib

SQL_PATH = os.path.join(os.getcwd(),"wego.db")
con = sqlite3.connect(SQL_PATH)

# @route('/hello')
# @route('/hello/<name>')
@route('/userinfo')
def handle_userinfo():
    userid = request.query.userid
    key = request.query.key
    value = request.query.value
    if(userid!="" and key!="userid" and key!="username" and key!="password" and key!="isused" and key!="la_label" and key!="ny_label"):
        try:
            con.execute("update user set "+key+" = (?)",[value])
            con.commit()
            data = {"text":"Edit successfully","code":"OK"}
            return json.dumps(data)
        except:
            data = {"text":"Invaild Request","code":"Error"}
            return json.dumps(data)
    else:
        data = {"text":"Invaild Request","code":"Error"}
        return json.dumps(data)


@route('/userhome')
def do_getuserhome():
    userid = request.query.userid
    if(userid!=""):
        try:
            c = con.cursor()
            c.execute("select userid,username,gender,homecity from user where userid = (?)",[userid])
            basicinfo = c.fetchall()
            c = con.cursor()
            c.execute("select E.categoryname,F.* from category as E join (select C.* ,D.createtime from venue as C join (select venueid,createtime from tip as A join (select * from user where user.userid =(?)) as B on A.userid = B.userid) as D on C.venueid = D.venueid order by D.createtime desc) as F on E.categoryid = F.category limit 10",[userid])
            recenthistory = c.fetchall()
            recenthistory_format=[]
            for item in recenthistory:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6],"createtime":item[11]}
                recenthistory_format.append(item_json)
            c = con.cursor()
            c.execute("select count(userb) as uesrbcount from friendship where usera = (?)",[userid])
            following = c.fetchall()
            c = con.cursor()
            c.execute("select count(usera) as uesracount from friendship where userb = (?)",[userid])
            followers = c.fetchall()
            data = {"userid":basicinfo[0][0],"username":basicinfo[0][1],"gender":"Male" if(basicinfo[0][2]==1) else "Female",
            "city":basicinfo[0][3],"history":recenthistory_format,"following":following[0][0],"followers":followers[0][0]}
            return json.dumps(data)
        except:
            data = {}
            return json.dumps(data)
    else:
        data = {}
        return json.dumps(data)


@route('/friendship')
def do_handlefrienship():
    usera = request.query.usera    
    userb = request.query.userb
    action = request.query.action
    if (usera!="" and userb!="" and usera!=userb):
        try:
            if(action=="add"):
                con.execute('insert into friendship(usera,userb) values(?,?)',[usera,userb])
                con.commit()
                data = {"text":"Add successful", "code":"OK"}
                return json.dumps(data)
            elif(action=="del"):
                con.execute('delete from friendship where usera=(?) and userb=(?)',[usera,userb])
                con.commit()
                data = {"text":"Delete successful", "code":"OK"}
                return json.dumps(data)
            else:
                data = {"text":"Invaild Request","code":"Error"}
                return json.dumps(data)
        except:
            data = {"text":"Operation failed, place try again", "code":"Error"}
            return json.dumps(data)
    else:
        data = {"text":"Invaild Request","code":"Error"}
        return json.dumps(data)

@route('/friendlist')
def do_getfriendlist():
    userid = request.query.userid
    action = request.query.action
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
                data = {"result":result_format}
                return json.dumps(data)
            elif(action=="followers"):
                c = con.cursor()
                c.execute("select userid,username,gender,homecity from user where userid in (select usera from friendship where userb = (?)) limit 100",[userid])
                result = c.fetchall()
                result_format=[]
                for item in result:
                    item_json = {"userid":item[0],"username":item[1],"gender":"Male" if(item[2]==1) else "Female","homecity":item[3]}
                    result_format.append(item_json)
                data = {"result":result_format}
                return json.dumps(data)
            else:
                data = {"text":"Invaild Request","code":"Error"}
                return json.dumps(data) 
        except:
            data = {"text":"Operation failed, place try again", "code":"Error"}
            return json.dumps(data)
        
    else:
        data = {"text":"Invaild Request","code":"Error"}
        return json.dumps(data)

@route('/searchfriend')
def handle_search_friend():
    keyword = request.query.keyword
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
            data = {"result":result_format}
            return json.dumps(data)
        except:
            data = {"text":"Operation failed, place try again", "code":"Error"}
            return json.dumps(data)
    else:
        data = {"text":"Invaild Request","code":"Error"}
        return json.dumps(data)









@route('/login',method='POST')
def do_login():
    # m = hashlib.sha256()
    username = request.forms.get('username')
    password = request.forms.get('password')

    # m.update(password.encode(encoding='utf-8'))

    check_response = check_login(username,password)
    print(check_response)
    if (check_response!={}):
        # response.set_cookie("account",username,secret='wego')
        data = {"text":"Login successful", "code":"OK", "user":{"userid":check_response['userid'],"username":check_response['username']}}
        return json.dumps(data)
    else:
        data = {"text":"Login failed", "code":"Error"}
        return json.dumps(data)

@route('/register', method='POST')
def do_register():
    # m = hashlib.sha256()
    userid = int(round(time.time() * 1000))
    username = request.forms.get('username')
    password = request.forms.get('password')
    email = request.forms.get('email')
    # m.update(password.encode(encoding='utf-8'))
    gender = True
    
    try:
        con.execute('insert into user(userid,username,password,email,gender) values(?,?,?,?,?)',[userid,username,password,email,gender])
        con.commit()
        data = {"text":"Register successful", "code":"OK"}
        return json.dumps(data)
    except:
        data = {"text":"Please choose another username", "code":"Error"}
        return json.dumps(data)
@route('/recommend')
def do_recommend():
    userid = request.query.userid
    # 0-3: weekday 4-7:weekend 0\4:morning 1\5:afternoon 2\6:evening 3\7:midnight
    timeid = request.query.timeid
    lat = request.query.lat
    lon = request.query.lon
    city = request.query.city
    try:
        c = con.cursor()
        if(city=="LA"):
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where la_label!=-2) ) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 10")
        else:
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where ny_label!=-2) ) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 10")                
        result = c.fetchall()
        result_format = []
        for item in result:
            item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
            result_format.append(item_json)
    except:
        result_format = []
    data = {"result":result_format}
    return json.dumps(data)     
    

@route('/search')
def do_search():
    city = request.query.city
    keyword = request.query.keyword    
    if(keyword=="restaurant"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '3' or categoryid='3') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '3' or categoryid='3') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data) 
    elif(keyword=="mall"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d1fd941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d1fd941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data) 
    elif(keyword=="nightlife"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid ='6' or categoryid = '6') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid ='6' or categoryid = '6') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)    
    elif(keyword=="hotel"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d1f0941735' or categoryid='4bf58dd8d48988d1fa931735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d1f0941735' or categoryid='4bf58dd8d48988d1fa931735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)       
    elif(keyword=="park"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d182941735', '4bf58dd8d48988d193941735', '4bf58dd8d48988d163941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d182941735', '4bf58dd8d48988d193941735', '4bf58dd8d48988d163941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)
    elif(keyword=="movie"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d17f941735' or categoryid='4bf58dd8d48988d17f941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d17f941735' or categoryid='4bf58dd8d48988d17f941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)
    elif(keyword=="museum"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d181941735' or categoryid='4bf58dd8d48988d181941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d181941735' or categoryid='4bf58dd8d48988d181941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)
    elif(keyword=="stadium"):
        try:
            c = con.cursor()
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d184941735' or categoryid='4bf58dd8d48988d184941735' or parentid ='4bf58dd8d48988d1b4941735' or categoryid='4bf58dd8d48988d1b4941735') and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d184941735' or categoryid='4bf58dd8d48988d184941735' or parentid ='4bf58dd8d48988d1b4941735' or categoryid='4bf58dd8d48988d1b4941735') and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)
    else:
        try:
            c = con.cursor()
            keyword = '%' + keyword + '%'
            if(city=="LA"):
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where venuename like (?) and la_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50",[keyword])
            else:
                c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where venuename like (?) and ny_label!=-2) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50",[keyword])                
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)
@route('/history')
def do_handlehistory():
    userid=request.query.userid
    try:
        c = con.cursor()
        c.execute("select E.categoryname,F.* from category as E join (select C.* ,D.createtime from venue as C join (select venueid,createtime from tip as A join (select * from user where user.userid =(?)) as B on A.userid = B.userid) as D on C.venueid = D.venueid order by D.createtime desc) as F on E.categoryid = F.category limit 100",[userid])
        result = c.fetchall()
        result_format = []
        for item in result:
            item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6],"createtime":item[11]}
            result_format.append(item_json)
    except:
        result_format = []
    data = {"result":result_format}
    return json.dumps(data)
    
@route('/sign')
def do_handlesign():
    userid = request.query.userid
    venueid = request.query.venueid
    try:
        createtime = time.time()
        con.execute('insert into tip(userid,venueid,createtime) values(?,?,?)',[userid,venueid,createtime])
        con.commit()
        data = {"text":"Sign successful", "code":"OK"}
        return json.dumps(data)
    except:
        data = {"text":"Sign failed, place try again", "code":"Error"}
        return json.dumps(data)

@route('/favorite')
def do_handlefavorite():
    userid = request.query.userid
    venueid = request.query.venueid
    action = request.query.action
    if(action == "add"):
        try:
            createtime = time.time()
            con.execute('insert into favorite(userid,venueid,createtime) values(?,?,?)',[userid,venueid,createtime])
            con.commit()
            data = {"text":"Add successful", "code":"OK"}
            return json.dumps(data)
        except:
            data = {"text":"This place has been added in your favorite", "code":"Error"}
            return json.dumps(data)
    elif(action == "delete"):
        try:
            con.execute('delete from favorite where userid=(?) and venueid=(?)',[userid,venueid])
            con.commit()
            data = {"text":"Delete successful", "code":"OK"}
            return json.dumps(data)
        except:
            data = {"text":"This place has not been added in your favorite", "code":"Error"}
            return json.dumps(data)            
    else:
        try:
            c = con.cursor()
            c.execute("select A.categoryname,B.* from category as A join (select * from venue where venueid in (select venueid from favorite where userid=(?))) as B on A.categoryid = B.category",[userid])
            result = c.fetchall()
            result_format = []
            for item in result:
                item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
                result_format.append(item_json)
        except:
            result_format = []
        data = {"result":result_format}
        return json.dumps(data)

@route('/positioninfo')
def do_getpositioninfo():
    userid = request.query.userid
    venueid = request.query.venueid
    if(userid and venueid):
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
            data = {}
        return json.dumps(data)
    return

@route('/iflogin')
def iflogin():
    username = request.get_cookie("account",secret='wego')
    if username:
        return template('Welcome back, {{name}}',name=username)
    else:
        redirect('/login')

@route('/logout')
def do_logout():
    response.delete_cookie("account")
    return "Logout successfully"

def check_login(username,password):
    print(username,password)
    
    try:
        c = con.cursor()
        c.execute("select * from user where username=(?)",[username])
        result = c.fetchall()
        if password == result[0][2]:
            return {'userid':result[0][0],'username':result[0][1]}
        else:
            return {}
    except:
        return {}

run(reloader=True, host='0.0.0.0', port=8088)
