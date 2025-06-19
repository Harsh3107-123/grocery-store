# flask in package name and all above imports are required for the Flask application to run and they are basically classes and functions
from flask import Flask
# create an instance of the Flask class
app = Flask(__name__)

# define a route for the root URL
@app.route('/')
def home():
    return "Hello, World!"
