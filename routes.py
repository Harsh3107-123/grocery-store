from app import app
# flask in package name and all above imports are required for the Flask application to run and they are basically classes and functions
from flask import render_template,request,redirect,url_for,flash,session
# render_template is used to render the HTML templates, request is used to handle incoming requests,
# define a route for the root URL


# now import some important stuff from models for backend validation
# it is good practise to  import only those things which are required in the file
from models import *

# for security important stuff from  werkzeug.security
from werkzeug.security import generate_password_hash,check_password_hash

from functools import wraps
import csv
from uuid import uuid4
from datetime import datetime

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
    
    user=User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))

    return redirect(url_for('home'))

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

#adding another decorator  to check whether the user is admin or not
def admin_required(f):
    @wraps(f)
    def admin_decorator(*args,**Kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        user=User.query.get(session['user_id'])
        if not user.is_admin :
            flash("Your are not authorised to enter into admin pannel")
            return redirect(url_for('login'))
        return f(*args, **Kwargs)
    return admin_decorator

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
    return redirect(url_for('home'))
#adding logout button in here
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

#it is route for home page
@app.route('/home')
@login_required
def home():
    user=User.query.get(session['user_id'])
    categories=Category.query.all()
    
    cname=request.args.get('cname') or ''
    pname=request.args.get('pname') or ''
    price=request.args.get('price')
    
    if price:
        try:
            price=float(price)
        except ValueError:
            flash("Invalid price")
            return redirect(url_for('home'))    
        if price <=0:
            flash("Invalid price")
            return redirect(url_for('home'))
            
    
    if cname:
        categories=Category.query.filter(Category.name.ilike(f"%{cname}%")).all()
        
    return render_template('home.html',user=user,categories=categories,cname=cname,pname=pname,price=price)


@app.route('/admin')
@admin_required
def admin():
    categories=Category.query.all()
    category_names=[category.name for category in categories]
    category_sizes=[len(category.products) for category in categories]
    return render_template('admin.html',categories=categories,category_names=category_names,category_sizes=category_sizes)

@app.route('/category/add')
@admin_required
def add_category():
    return render_template('category/add.html')


@app.route('/category/add',methods=['POST'])
@admin_required
def add_category_post():
    name=request.form.get('name')
    categories=Category.query.all()
    
    for category in categories:
        if name==category.name:
            flash("Category already exist") 
            return redirect(url_for('add_category'))
    category=Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash("Category added successfully")
    return redirect(url_for('admin'))

@app.route('/category/<int:id>')
@admin_required
def show_category(id):
    category=Category.query.get(id)
    if not category:
        flash("Category does not exists")
        return redirect(url_for('admin'))
    return render_template('category/show.html',category=category)

@app.route('/category/<int:id>/edit')
@admin_required
def edit_category(id):
    category=Category.query.get(id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('admin'))
    return render_template('category/edit.html',category=category)


@app.route('/category/<int:id>/edit',methods=['POST'])
@admin_required
def edit_category_post(id):
    category=Category.query.get(id)
    name=request.form.get('name')
    categories=Category.query.all()
    for category in categories:
        if name in category.name:
            flash("Category already exist")
            return redirect(url_for('admin'))
    category.name=name
    db.session.commit()
    flash('Updated successfully')
    return redirect(url_for('admin'))


@app.route('/category/<int:id>/delete')
@admin_required
def delete_category(id):
    category=Category.query.get(id)
    return render_template('category/delete.html',category=category)

@app.route('/category/<int:id>/delete',methods=['POST'])
@admin_required
def delete_category_post(id):
    category=Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    flash("category is deleted")
    return redirect(url_for('admin'))

@app.route('/product/add/<int:category_id>')
@admin_required
def add_product(category_id):
    categories=Category.query.all()
    return render_template('products/add.html',categories=categories,category_id=category_id)

@app.route('/product/add/<int:category_id>',methods=['POST'])
@admin_required
def add_product_post(category_id):
    name=request.form.get('name')
    price=request.form.get('price')
    quantity=request.form.get('quantity')
    man_date_str=request.form.get('man_date')
    man_date=datetime.strptime(man_date_str, '%Y-%m-%d').date()
    
    category=Category.query.get(category_id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('admin'))  
    
    products=Product.query.all()
    for product in products:
        if name==product.name:
            flash("Product already exist") 
            return redirect(url_for('add_category'))
    try:
        price=float(price)
        quantity=int(quantity)
    except ValueError:
        flash("please provide valid price and quantity")
        return redirect(url_for('add_product',category_id=category.id))
    
    if price <= 0 or quantity <= 0:
        flash("Price and quantity must be greater than zero")
        return redirect(url_for('add_product', category_id=category.id))
    
    if man_date >= datetime.now().date():
        flash("Invalid Manufacture date")
        return redirect(url_for('add_product', category_id=category.id))
    
    product=Product(name=name,price=price,quantity=quantity,man_date=man_date,category_id=category_id)
    
    db.session.add(product)
    db.session.commit()
    flash("Product added successfully")
    return redirect(url_for('admin'))




@app.route('/product/<int:id>/edit')
@admin_required
def edit_product(id):
    product=Product.query.get(id)
    categories=Category.query.all()
    return render_template('products/edit.html',product=product,categories=categories)

@app.route('/product/<int:id>/edit',methods=["POST"])
@admin_required
def edit_product_post(id):
    product=Product.query.get(id)
    name=request.form.get('name')
    price=request.form.get('price')
    quantity=request.form.get('quantity')
    man_date_str=request.form.get('man_date')
    man_date=datetime.strptime(man_date_str, '%Y-%m-%d').date()
    
    category=Category.query.get(product.category_id)
    if not category:
        flash("Category does not exist")
        return redirect(url_for('admin'))  
    
    products=Product.query.all()
    for product in products:
        if name==product.name:
            flash("Product already exist") 
            return redirect(url_for('add_category'))
    try:
        price=float(price)
        quantity=int(quantity)
    except ValueError:
        flash("please provide valid price and quantity")
        return redirect(url_for('edit_product',id=product.id))
    
    if price <= 0 or quantity <= 0:
        flash("Price and quantity must be greater than zero")
        return redirect(url_for('edit_product',id=product.id))
    
    if man_date >= datetime.now().date():
        flash("Invalid Manufacture date")
        return redirect(url_for('add_product', category_id=category.id))
    
    product.name=name
    product.price=price
    product.quantity=quantity
    product.man_date=man_date
    product.category_id=request.form.get('category_id')
    
    db.session.commit()
    flash("Product updates successfully")
    return redirect(url_for('admin'))

@app.route('/product/<int:id>/delete')
@admin_required
def delete_product(id):
    product=Product.query.get(id)
    return render_template('products/delete.html',product=product)

@app.route('/product/<int:id>/delete',methods=['POST'])
@admin_required
def delete_product_post(id):
    product=Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    flash("category is deleted")
    return redirect(url_for('admin'))

@app.route('/add_to_cart/<int:product_id>',methods=['POST'])
@login_required
def add_to_cart(product_id):
    product=Product.query.get(product_id)
    if not product:
        flash("Product does not exist")
        return redirect(url_for('index'))
    quantity=request.form.get('quantity')
    try:
        quantity=int(quantity)
    except ValueError:
        flash('Invalid quantity')
        return redirect(url_for('index'))
    if quantity<=0 or quantity > product.quantity:
        flash(f'Invalid quantity should be between 1 and {product.quantity}')    
        return redirect(url_for('index'))
    
    cart=Cart.query.filter_by(user_id=session['user_id'],product_id=product_id).first()
    
    if cart:
        if quantity+cart.quantity>product.quantity:
            flash(f"Invlaid quantity, Should be between 1 and {product.quantity} ")
            return redirect(url_for('index'))
        cart.quantity+=quantity
    else:
        cart=Cart(user_id=session['user_id'],product_id=product.id,quantity=quantity)
        db.session.add(cart)
    db.session.commit()
    flash('product is added successfully to cart')
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    carts=Cart.query.filter_by(user_id=session['user_id']).all()
    total_amount = sum([cart.product.price * cart.quantity for cart in carts])
    return render_template('cart.html',carts=carts,total_amount=total_amount)

@app.route('/cart/<int:id>/delete',methods=['POST'])
@login_required
def delete_cart(id):
    cart=Cart.query.get(id)
    if not cart:
        flash("You do not have a cart with this id")
        return redirect(url_for('cart'))
    if cart.user_id!=session['user_id']:
        flash("Your are not authorised")
        return redirect(url_for('cart'))
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout',methods=['POST'])
@login_required
def checkout():
    carts = Cart.query.filter_by(user_id=session['user_id']).all()
    if not carts:
        flash('Cart is empty')
        return redirect(url_for('cart'))

    transaction = Transaction(user_id=session['user_id'], datetime=datetime.now())
    for cart in carts:
        order = Order(
        transaction=transaction,
        user_id=session['user_id'],  # use 'user_id', not 'user'
        product_id=cart.product.id,  # use product_id, not product
        quantity=cart.quantity,
        price=cart.product.price
    )
        if cart.product.quantity < cart.quantity:
            flash(f'Product {cart.product.name} is out of stock')
            return redirect(url_for('delete_cart', id=cart.id))
        cart.product.quantity -= cart.quantity
        db.session.add(order)
        db.session.delete(cart)
    db.session.add(transaction)
    db.session.commit()

    flash('Order placed successfully')
    return redirect(url_for('orders'))

@app.route('/orders')
@login_required
def orders():
    transactions = Transaction.query.filter_by(user_id=session['user_id']).order_by(Transaction.datetime.desc()).all()
    return render_template('orders.html', transactions=transactions)

@app.route('/export_csv')
@login_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=session['user_id'])
    filename=uuid4().hex+'.csv'
    url='static/csv/'+filename
    with open(url,'w',newline='') as file:
        writer=csv.writer(file)
        writer.writerow(['transaction_id','product_name', 'quantity', 'price', 'datetime'])
        for transaction in transactions:
            for order in transaction.orders:
                writer.writerow([transaction.id, order.product.name, order.quantity, order.price, transaction.datetime])
    return redirect(url_for('static', filename='csv/'+filename))