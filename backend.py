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

@route('/login',method='POST')
def do_login():
    # m = hashlib.sha256()
    username = request.forms.get('username')
    password = request.forms.get('password')

    # m.update(password.encode(encoding='utf-8'))

    if check_login(username,password):
        # response.set_cookie("account",username,secret='wego')
        data = {"text":"Login successful", "code":"OK"}
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

@route('/search')
def do_search():
    #TODO: 去掉 lat, lon, time
    #TODO: 增加 city 判断
    city = request.query.city
    latitude = request.query.latitude
    longitude = request.query.longitude
    time = request.query.time
    keyword = request.query.keyword    
    if(keyword=="restaurant"):
        try:
            c = con.cursor()
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '3' or categoryid='3')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d1fd941735')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid ='6' or categoryid = '6')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d1f0941735' or categoryid='4bf58dd8d48988d1fa931735')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in ('4bf58dd8d48988d182941735', '4bf58dd8d48988d193941735', '4bf58dd8d48988d163941735')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d17f941735' or categoryid='4bf58dd8d48988d17f941735')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d181941735' or categoryid='4bf58dd8d48988d181941735')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
            c.execute("select B.categoryname,C.* from category as B join(select A.* from venue as A join (select venueid from tip where venueid in (select venueid from venue where category in (select categoryid from category where parentid = '4bf58dd8d48988d184941735' or categoryid='4bf58dd8d48988d184941735' or parentid ='4bf58dd8d48988d1b4941735' or categoryid='4bf58dd8d48988d1b4941735')) group by venueid order by count(venueid) desc) as B on A.venueid = B.venueid) as C on B.categoryid = C.category limit 50")
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
        c.execute("select E.categoryname,F.* from category as E join (select C.* from venue as C join (select venueid,createtime from tip as A join (select * from user where user.userid =(?)) as B on A.userid = B.userid) as D on C.venueid = D.venueid order by D.createtime desc) as F on E.categoryid = F.category limit 100",[userid])
        result = c.fetchall()
        result_format = []
        for item in result:
            item_json = {"category":item[0],"venueid":item[1],"venuename":item[2],"latitude":item[4],"longitude":item[5],"address":item[6]}
            result_format.append(item_json)
    except:
        result_format = []
    data = {"result":result_format}
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
        c.execute("select password from user where username=(?)",[username])
        result = c.fetchall()
        if password == result[0][0]:
            return True
        else:
            return False
    except:
        return False

run(reloader=True, host='0.0.0.0', port=8088)
