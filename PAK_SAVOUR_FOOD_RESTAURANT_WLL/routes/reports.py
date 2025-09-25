from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime
from models import Order, Expense
from utils.currency import format_currency

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/")
@login_required
def reports():
    if not current_user.is_admin:
        return redirect("/")

    today = datetime.today().date()
    month = today.month
    year = today.year

    daily_sales = sum(o.total_price for o in Order.query.all() if o.created_at.date() == today)
    monthly_sales = sum(o.total_price for o in Order.query.all()
                        if o.created_at.month == month and o.created_at.year == year)

    expenses = Expense.query.all()
    total_expenses = sum(e.amount for e in expenses)

    return render_template("admin/reports.html",
                           daily_sales=format_currency(daily_sales),
                           monthly_sales=format_currency(monthly_sales),
                           expenses=expenses,
                           currency_symbol="$")
