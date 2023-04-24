#from app import app
from main import app, db, login_manager, getuser
import flask_login
from flask_login import current_user
import flask
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, UserMixin
import hashlib
import datetime
import re


class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = id



@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html', msg="", user=getuser())

# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)




@app.route('/logout')
# We could probably delete this function
def logout():
    flask_login.logout_user()
    return render_template('login.html', msg="You have been logged out. ", user=getuser())

# We could probably delete these functions.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html', user=getuser())
    print(request.form['password'])
    print(request.form['username'])

    if db.authenticate_user(password=request.form['password'], username=request.form['username']):
        user = User(request.form['username'])
        flask_login.login_user(user)
        return redirect('/')
    return render_template('login.html', err="The username or password is incorrect.", user=getuser())

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if flask.request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        username_pattern = "^[a-zA-Z0-9]{4,20}$"
        if password != password_confirm:
            return render_template("signup.html", user=getuser(), err='Passwords do not match')
        if db.check_user(username):
            return render_template("signup.html", user=getuser(), err=f'Username "{username}" already exists.')
        if not re.match(password_pattern, password):
            return render_template("signup.html", user=getuser(), err='Password does not meet requirements')
        if not re.match(username_pattern, username):
            return render_template("signup.html", user=getuser(), err='Username does not meet requirements')

        # In this case , we are good to add a new user to the database, then log the new user in.

        db.add_multirow_structure('users', [
            {
                'user_id': db.generateNewUniqueUserID(),
                'user_name': username,
                'pass_hash': str(hashlib.sha256(password.encode()).hexdigest()),
                'last_login': str(datetime.datetime.now())
            }
        ])

        return render_template("login.html", user=getuser(), err='Account created. Please log in.')

    #db.create_user(username, password)
    if flask.request.method == 'GET':
        return render_template("signup.html", user=getuser(), err='')