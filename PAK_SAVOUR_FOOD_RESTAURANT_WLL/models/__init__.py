from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered
from .user import User
from .product import Product
from .order import Order, OrderItem
from .expense import Expense
