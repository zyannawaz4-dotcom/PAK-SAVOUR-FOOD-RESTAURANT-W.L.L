from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Product

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for("pos.pos"))
    return render_template("admin/admin_dashboard.html")

@admin_bp.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if not current_user.is_admin:
        return redirect(url_for("pos.pos"))
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form.get("description")
        image = request.form.get("image")

        product = Product(name=name, price=price, description=description, image=image)
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/admin_add_product.html")
