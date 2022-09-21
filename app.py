from flask import (Flask, after_this_request, flash, jsonify, redirect, render_template, request, session, url_for)
import os
from datetime import date, datetime, timedelta , time
import calendar
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

UPLOAD_FOLDER = '/static/assets/employee'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#encryption relies on secret keys so they could be run
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://gazing:akshay302@cluster0.aooyowx.mongodb.net/test?retryWrites=true&w=majority")

db = client.get_database('total_records')

records = db.users

team = db.employees

attend = db.attendence

# mydict =  { "email": "admin@gmail.com", "password": "akshay" }

# x = records.insert_one(mydict)

#_______________________________________________________________________



@app.route("/")
def index():
    if not session.get('_id'):
            return redirect("/login")
    now = date.today()
    time = now.strftime("%I:%M:%S")
    CurrentDate = now.strftime("%d/%m/%Y")    
    emp_list = team.find({'username': session['username']}) 
    attend_list = attend.find({'username': session['username']},sort=[( "date", pymongo.DESCENDING)]).limit(1);
    Result = attend.find_one({'user_id': session['_id']},{'date':1 , '_id':0},sort=[( "date", pymongo.DESCENDING)])
    Today = {'date': CurrentDate}
    print(Result)
    print(Today)
    if (Result == Today):
        print('True')
    else:
        print('False')
    # print(exit())
    return render_template('index.html', time = time, Today = Today , Result = Result , attend_list = attend_list, emp_list = emp_list)
 
@app.route("/login", methods=["POST", "GET"]) 
def login():
    if "_id" in session:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #check if username exists in database
        username_found = team.find_one({"username": username})
        if username_found:
            username_val = username_found['username']  
            passwordcheck = username_found['password']
            user_id = username_found['_id']

            #encode the password and check if it matches
            if(password==passwordcheck):
                session["_id"] = str(user_id)
                session["username"] = username_val
                return redirect("/")
            else:
                if "_id" in session:
                    return redirect("/")
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'username not found'
            return render_template('login.html', message=message)
        
    return render_template('login.html')

@app.route("/attendence")
def attendence():
    if not session.get('_id'):
        return redirect("/login")
    attend_list = attend.find({'username': session['username']})      
    return render_template('attendence.html',attend_list = attend_list )
 
@app.route('/punch-in')
def punch_in():  
    if not session.get('_id'):
        return redirect("/login")
    now = datetime.now()
    punch_in = now.strftime("%I:%M:%S")
    date = now.strftime("%d/%m/%Y")
    month = now.month
    emp_list = team.find({'username': session['username']}) 
    username = session['username']
    user_id = session['_id']
    attend_list = attend.find({'username': session['username']} ) 
    attend.insert_one({"username":username, "month": month, "user_id": user_id,"date":date , "punch_in": punch_in })
    return redirect("/")
    return render_template('index.html' , punch_in = punch_in , emp_list = emp_list,attend_list = attend_list ,message = message , now = now)

@app.route('/break-start')
def break_start():
    now = datetime.now()
    break_start = now.strftime("%I:%M:%S")
    id=request.values.get("_id")
    attend.find({"_id":ObjectId(id)})
    attend.update_one({"_id":ObjectId(id)},
                     {
                        "$set": {  "break_start": break_start }
                    
                    }, upsert=True)
    return redirect("/")
    return render_template('index.html')
 
@app.route('/break-end')
def break_end():
    now = datetime.now()
    break_end = now.strftime("%I:%M:%S")
    id=request.values.get("_id")
    attend.find({"_id":ObjectId(id)})
    attend.update_one({"_id":ObjectId(id)},
                     {
                        "$set": {  "break_end": break_end}
                    
                    }, upsert=True)         
    return redirect("/")
    return render_template('/index.html')


@app.route('/punch-out')
def punch_out():
    if not session.get('_id'):
        return redirect("/login")
    now = datetime.now()
    punch_out = now.strftime("%I:%M:%S")
    id=request.values.get("_id")
    attend.find({"_id":ObjectId(id)})
    attend.update_one({"_id":ObjectId(id)},
                     {
                        "$set": {  "punch_out": punch_out }
                    
                    }, upsert=True)
    return redirect("/")
    return render_template('index.html',emp_list = emp_list, punch_out = punch_out)


@app.route("/apply-leaves")
def apply_leaves():
    if not session.get('_id'):
        return redirect("/login")
    return render_template('apply-leaves.html')

@app.route("/my-leaves")
def my_leaves():
    if not session.get('_id'):
        return redirect("/login")
    return render_template('my-leaves.html')


@app.route("/profile", methods=["GET","POST"])
def profile():
    if not session.get('_id'):
        return redirect("/login")  
    emp_list = team.find({'username': session['username']})
    return render_template("profile.html", emp_list=emp_list)

@app.route("/profile-edit")
def profile_edit():
    if not session.get('_id'):
        return redirect("/login")
    emp_list=team.find({'username': session['username']}) 
    return render_template('profile-edit.html', emp_list=emp_list)


@app.route('/updatedata', methods=['POST', 'GET'])
def updatedata():
    id=request.values.get("_id")
    team.find({"_id":ObjectId(id)})
    team.update_one({"_id":ObjectId(id)},
                 {
                     "$set": {
                              "fname": request.form.get('fname'),
                              "lname": request.form.get('lname'),
                              "phone": request.form.get('phone'),
                              "email": request.form.get('email'),
                              "password": request.form.get('password'),
                              "profilepic": request.form.get('profilepic'),
                              }
                 }, upsert=True)
    return redirect("/profile")


@app.route('/logout')
def logout():
    session.pop('_id',None)
    return redirect(url_for('login'))


# ___ ADMIN ____________________akshay naithani______________________________

@app.route("/admin")
def admin():
    if not session.get("email"):
        return redirect("/admin-login")
    return render_template('admin-dashboard.html')

  

@app.route("/admin-login", methods=["POST", "GET"])
def adminlogin():
    if "email" in session:
        return redirect("/admin")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if username exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
          
            #encode the password and check if it matches
            if(password==passwordcheck):
                session["email"] = email_val
                return redirect("/admin")
            else:
                if "email" in session:
                    return redirect("/admin-dashboard")
                message = 'Wrong password'
                return render_template('admin-login.html', message=message)
        else:
            message = 'email not found'
            return render_template('admin-login.html', message=message)
    return render_template('admin-login.html')
    

@app.route("/change-password")
def adminchange_password():
    if not session.get("email"):
            return redirect("/admin-login") 
    id=request.values.get("_id")
    emp_list=team.find({"_id":ObjectId(id)})
    return render_template('admin-changepassword.html', emp_list = emp_list)

@app.route('/password-changed', methods=['POST', 'GET'])
def password_changed():
    if not session.get("email"):
            return redirect("/admin-login") 
    id=request.values.get("_id")
    records.find({"_id":ObjectId(id)})
    records.update_one({"_id":ObjectId(id)},
                 {
                     "$set": {
                              "password": request.form.get('password'),
                              }
                 }, upsert=True)
    return redirect("/admin")

@app.route("/add-employee")
def add_employee():
        if not session.get("email"):
              return redirect("/admin-login")    
        return render_template('add-employee.html')

@app.route("/employees", methods=["GET", "POST"] )
def employees():
        if not session.get("email"):
              return redirect("/admin-login")          
        employees = {}
        if request.method == "POST":
            employees['fname'] = request.form['fname']
            employees['lname'] = request.form['lname']
            employees['phone'] = request.form['phone']
            employees['email'] = request.form['email']
            employees['employeeid'] = request.form['employeeid']
            employees['joining'] = request.form['joining']
            employees['designation'] = request.form['designation']
            employees['salary'] = request.form['salary']
            employees['username'] = request.form['username']
            employees['password'] = request.form['password']
            employees['profilepic'] = request.form['profilepic']
        team.insert_one(employees)
        return redirect("/all-employees")

@app.route("/all-employees")
def all_employees():
       if not session.get("email"):
              return redirect("/admin-login")    
       emp_list = team.find()
       return render_template('all-employees.html' , emp_list = emp_list)


@app.route("/edit-employee")
def edit_employee ():
	id=request.values.get("_id")
	emp_list=team.find({"_id":ObjectId(id)})
	return render_template('edit-employee.html',emp_list=emp_list)

@app.route('/updateemp', methods=['POST', 'GET'])
def updateemp():
    id=request.values.get("_id")
    team.find({"_id":ObjectId(id)})
    team.update_one({"_id":ObjectId(id)},
                 {
                     "$set": {
                              "fname": request.form.get('fname'),
                              "lname": request.form.get('lname'),
                              "phone": request.form.get('phone'),
                              "email": request.form.get('email'),
                              "employeeid": request.form.get('employeeid'),
                              "joining": request.form.get('joining'),
                              "designation": request.form.get('designation'),
                              "salary": request.form.get('salary'),
                              "username": request.form.get('username'),
                              "password": request.form.get('password'),
                              }
                 }, upsert=True)
    return redirect("/all-employees")

@app.route("/remove-employee")    
def remove():    
    key=request.values.get("_id")    
    team.delete_one({"_id":ObjectId(key)})    
    flash('Employee deleted successfully') 
    return redirect("/all-employees")

@app.route("/today-attendence")
def today_attendence():
    if not session.get("email"):
        return redirect("/admin-login")
    emp_list = team.find()
    attend_list = attend.find()
    return render_template('today-attendence.html' ,attend_list = attend_list ,emp_list = emp_list)

@app.route("/attendence-sheet")
def attendence_sheet():
    if not session.get("email"):
        return redirect("/admin-login")
    emp_list = team.find()
    attend_list = attend.find()
    return render_template('attendence-sheet.html' ,attend_list = attend_list ,emp_list = emp_list)
 

@app.route('/admin-logout')
def adminlogout():
    session.pop('email',None)
    return redirect(url_for('adminlogin'))



if __name__ == "__main__":
      app.run(debug=True)
