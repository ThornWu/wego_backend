from bottle import route, run, template, request, redirect, response
import sqlite3
# import hashlib
import os
import json

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

@route('/register')
def register():
    return '''
        <form action="/register" method="post">
            Username: <input name="username" type="text"/>
            <br/>
            Password: <input name="password" type="password"/>
            <br/>
            Reapeat password:<input type="password"/>
            <br/>
            Gender: <input name="gender" type="radio" value="man" checked/> Man
            <input name="gender" type= "radio" value="woman"/> Woman
            <br/>
            Homecity:<input name="homecity" type="radio" value="Los Angeles" checked/>Los Angeles
            <input name="homecity" type="radio" value="New York"/>New York
            <br/>
            <input value="register" type="submit"/>
        </form>
    '''
@route('/register', method='POST')
def do_register():
    # m = hashlib.sha256()
    username = request.forms.get('username')
    password = request.forms.get('password')
    # m.update(password.encode(encoding='utf-8'))
    gender = (request.forms.get('gender') == "man")
    homecity = request.forms.get('homecity') 
    try:
        con.execute('insert into user(username,password,gender,homecity) values(?,?,?,?)',[username,password,gender,homecity])
        con.commit()
    except:
        return "Error"
    else:
        return "OK"

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
