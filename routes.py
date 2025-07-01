from app import app
# flask in package name and all above imports are required for the Flask application to run and they are basically classes and functions
from flask import render_template,request,redirect,url_for,flash,session
# render_template is used to render the HTML templates, request is used to handle incoming requests,
# define a route for the root URL


# now import some important stuff from models for backend validation
# it is good practise to  import only those things which are required in the file
from models import User, db

# for security important stuff from  werkzeug.security
from werkzeug.security import generate_password_hash,check_password_hash

@app.route('/')
def index():
    #check if the user is in the session or not(we can say that it is a cookie) this will not allow us to enter in the index page directly
    if 'user_id' in session:
        return render_template("index.html")
    else :
        flash('please login first')
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login',methods=['POST'])
def login_post():
    username=request.form.get('loginname')
    password=request.form.get('loginpassword')
    if not username or not password:
        flash("Please fill all the necessary fields to login")
        return redirect(url_for('login'))
    
    #check if user exists or not
    user=User.query.filter_by(username=username).first()
    if not user:
        flash("User does not exist")
        return redirect(url_for('login'))
    
    # check if password is correct or not
    if not check_password_hash(user.passhash,password):
        flash("password is incorrect")
        return redirect(url_for('login'))
    
    # Now let us save the session id so that it can be authenciated successfully
    session['user_id']=user.id
    flash('Login Successfull')

    return redirect(url_for('index'))

# define route for the registeration of the user
@app.route('/register')
def register():
    return render_template("register.html")

#just for understanding purpose defining another route for register in order to understand post
@app.route('/register',methods=['Post'])
def register_post():
    username=request.form.get('username')
    password=request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    name=request.form.get('name')
    if not username or not password or not confirm_password :
        flash("Please fill all the fields")
        return redirect(url_for('register'))
    
    # check if passwoerd and confirm password are same
    if password != confirm_password:
        flash('password and confirm password are not same')
        return redirect(url_for('register'))
    
    # check if user already exists
    if User.query.filter_by(username=username).first():
        flash('User already exists')
        return redirect(url_for('register'))
    
    # hash the password using werkzeug security
    password=generate_password_hash(password)
    #create a new User object and save it to the database
    user=User(username=username,passhash=password,name=name)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))