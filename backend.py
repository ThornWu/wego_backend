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

@route('/logout')
def do_logout():
    response.delete_cookie("account")
    return "Logout successfully"

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

@route('/iflogin')
def iflogin():
    username = request.get_cookie("account",secret='wego')
    if username:
        return template('Welcome back, {{name}}',name=username)
    else:
        redirect('/login')

def check_login(username,password):
    print(username,password)
    
    try:
        c = con.cursor()
        c.execute("select password from user where username=(?)", (username,))
        result = c.fetchall()
        if password == result[0][0]:
            return True
        else:
            return False
    except:
        return False

run(reloader=True, host='0.0.0.0', port=8088)
