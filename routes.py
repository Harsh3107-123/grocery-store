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
from functools import wraps

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

#adding thing called decorator such that it will add additional functionality in our code so that we does not need to authenticate many times 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#Create a Profile of a user which will show the user about it's own self
@app.route('/profile')
@login_required
def profile():
        #fetch the user id from here
        user=User.query.get(session['user_id'])
        return render_template('profile.html',user=user)

@app.route('/profile',methods=['POST'])
@login_required
def profile_post():
        #fetch the user id from here
        username=request.form.get('username')
        curent_password=request.form.get('password')
        new_password=request.form.get('new_password')
        name=request.form.get('name')
        
        if not username or not curent_password or not new_password:
            flash('Please fill out all the necessaryu fields')
            return redirect(url_for('profile'))
        
        user=User.query.get(session['user_id'])
        if not check_password_hash(user.passhash,curent_password):
            flash('Enter correct current password')
            return redirect(url_for('profile'))
        
        if username !=user.username:
            new_username=User.query.filter_by(username=username).first()
            if new_username:
                flash('username already exists')
                return redirect(url_for('profile'))
            user.username=username
            passhash=generate_password_hash(new_password)
            user.passhash=passhash
            user.name=name
            db.session.commit()
            flash('changes are made successfully')
            return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    
    #check if the user is in the session or not(we can say that it is a cookie) this will not allow us to enter in the index page directly
    return render_template("index.html")

#adding logout button in here
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))