from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Product, Order, OrderItem

pos_bp = Blueprint("pos", __name__, url_prefix="/pos")

@pos_bp.route("/", methods=["GET", "POST"])
@login_required
def pos():
    products = Product.query.all()
    if request.method == "POST":
        customer = request.form.get("customer_name", "Walk-in")
        table = request.form.get("table_no", "N/A")
        payment = request.form.get("payment_method", "Cash")

        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        product = Product.query.get(product_id)
        total_price = product.price * quantity

        order = Order(customer_name=customer, table_no=table,
                      total_price=total_price, payment_method=payment)
        db.session.add(order)
        db.session.flush()  # to get order.id

        item = OrderItem(order_id=order.id, product_id=product.id,
                         quantity=quantity, price=product.price)
        db.session.add(item)
        db.session.commit()

        flash("Order placed successfully!")
        return redirect(url_for("pos.pos"))

    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/pos.html", products=products, orders=orders)
