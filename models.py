# we are not woking with a sql queries to directly inteereact with daatabase we are using orms to create a databasen 
#  it is better to make everything more pytghonic and use python classes to represent the database tables
from app import app
from flask_sqlalchemy import SQLAlchemy
# make instance of database (db)
db=SQLAlchemy(app)

#importing security stuff
from werkzeug.security import generate_password_hash

#creating user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
# creating category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    # It sets up a link so you can easily get all products in a category, and from a product, you can find its category.
    products = db.relationship('Product', backref='category', lazy=True,cascade="all, delete-orphan")

# creating product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    man_date = db.Column(db.Date, nullable=False)
    
    carts = db.relationship('Cart', backref='cart', lazy=True)
    orders = db.relationship('Order', backref='order', lazy=True)

# creating cart model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

# creating transaction model 
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    orders = db.relationship('Order', backref='transaction', lazy=True)

# creating order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    #  creates all the database tables defined by your models (if they don’t already exist)
    db.create_all()
    #create admin ceredentialals
    admin=User.query.filter_by(is_admin=True).first()
    if not admin:
        password_hash=generate_password_hash('admin@123')
        admin=User(username='Admin',passhash=password_hash,is_admin=True)
        db.session.add(admin)
        db.session.commit()
