from app import app
# flask in package name and all above imports are required for the Flask application to run and they are basically classes and functions
from flask import render_template
# define a route for the root URL

@app.route('/')
def login():
    return render_template("login.html")

# define route for the registeration of the user
@app.route('/register')
def register():
    return render_template("register.html")
