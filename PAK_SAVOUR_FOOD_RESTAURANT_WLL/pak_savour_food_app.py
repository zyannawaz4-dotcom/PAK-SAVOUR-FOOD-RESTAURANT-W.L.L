import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

# Setup Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bd_pos_secret'

# Ensure instance folder exists
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Database
db_path = os.path.join(instance_dir, 'store.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CURRENCY_SYMBOL = ".د.ب"

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float)
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(255))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    wastage = db.Column(db.Integer, default=0)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(255))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=1)
    wastage = db.Column(db.Integer, default=0)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def home():
    products = Product.query.order_by(Product.name).all()
    cart_items = CartItem.query.all()
    cart_total = sum(item.price*item.quantity for item in cart_items)
    return render_template('home.html', products=products, cart_items=cart_items, total=cart_total, currency=CURRENCY_SYMBOL)

# Menu Management
@app.route('/menu')
def menu():
    products = Product.query.order_by(Product.name).all()
    return render_template('menu.html', products=products, currency=CURRENCY_SYMBOL)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        image = request.form.get('image')
        product = Product(name=name, price=price, image=image)
        db.session.add(product)
        db.session.commit()
        flash(f'Item "{name}" added.')
        return redirect(url_for('menu'))
    return render_template('add_item.html')

@app.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    product = Product.query.get_or_404(item_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.image = request.form.get('image')
        db.session.commit()
        flash(f'Item "{product.name}" updated.')
        return redirect(url_for('menu'))
    return render_template('edit_item.html', product=product)

@app.route('/menu/delete/<int:item_id>')
def delete_item(item_id):
    product = Product.query.get_or_404(item_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Item "{product.name}" deleted.')
    return redirect(url_for('menu'))

# POS / Cart
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    item = CartItem.query.filter_by(product_id=product.id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(product_id=product.id, product_name=product.name, price=product.price, quantity=1)
        db.session.add(item)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    for key, value in request.form.items():
        if key.startswith('qty_'):
            item_id = int(key.split('_')[1])
            item = CartItem.query.get(item_id)
            if item:
                item.quantity = int(value)
        if key.startswith('waste_'):
            item_id = int(key.split('_')[1])
            item = CartItem.query.get(item_id)
            if item:
                item.wastage = int(value)
    db.session.commit()
    flash('Cart updated.')
    return redirect(url_for('home'))

@app.route('/checkout', methods=['POST'])
def checkout():
    cart_items = CartItem.query.all()
    if not cart_items:
        flash('Cart is empty.')
        return redirect(url_for('home'))

    total = sum(item.price*item.quantity for item in cart_items)
    order = Order(total=total)
    db.session.add(order)
    db.session.commit()
    
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, product_name=item.product_name, price=item.price, quantity=item.quantity, wastage=item.wastage)
        db.session.add(order_item)
    db.session.commit()

    CartItem.query.delete()
    db.session.commit()
    flash('Checkout completed.')
    return redirect(url_for('home'))

# Reports
@app.route('/reports')
def reports():
    today = date.today()
    orders_today = Order.query.filter(db.func.date(Order.created_at) == today).all()
    total_sales = sum(o.total for o in orders_today)
    sold_items = {}
    for o in orders_today:
        for i in o.items:
            sold_items[i.product_name] = sold_items.get(i.product_name, 0) + i.quantity
    most_sold = sorted(sold_items.items(), key=lambda x: x[1], reverse=True)

    wastage_items = {}
    for o in orders_today:
        for i in o.items:
            wastage_items[i.product_name] = wastage_items.get(i.product_name, 0) + i.wastage

    return render_template('reports.html', orders=orders_today, total_sales=total_sales, most_sold=most_sold, wastage_items=wastage_items, currency=CURRENCY_SYMBOL)

# Expenses
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        exp = Expense(name=name, amount=amount)
        db.session.add(exp)
        db.session.commit()
        flash(f'Expense "{name}" added.')
        return redirect(url_for('expenses'))
    all_expenses = Expense.query.order_by(Expense.created_at.desc()).all()
    return render_template('expenses.html', expenses=all_expenses, currency=CURRENCY_SYMBOL)

# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
