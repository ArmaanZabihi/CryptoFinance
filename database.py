from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hash = db.Column(db.String(255), nullable=False)
    cash = db.Column(db.Numeric(precision=10, scale=2), nullable=False, default=1000.00)
    # Relationship - User can have many transactions
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, username, hash, cash=1000.0):
        self.username = username
        self.hash = hash
        self.cash = cash

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symbol = db.Column(db.String(255), nullable=False)
    shares = db.Column(db.Numeric(precision=10, scale=8), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id, symbol, shares, price):
        self.user_id = user_id
        self.symbol = symbol
        self.shares = shares
        self.price = price
