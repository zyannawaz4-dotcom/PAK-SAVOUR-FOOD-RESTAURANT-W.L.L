from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, Expense

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")

@expenses_bp.route("/", methods=["GET", "POST"])
@login_required
def expenses():
    if not current_user.is_admin:
        return redirect(url_for("pos.pos"))
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        expense = Expense(name=name, amount=amount)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for("expenses.expenses"))

    expenses = Expense.query.all()
    return render_template("admin/expenses.html", expenses=expenses)
