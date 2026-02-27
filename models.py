from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track when user was created
    
    def __repr__(self):
        return f'<User {self.username}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track when item was added
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Track updates
    
    def __repr__(self):
        return f'<Inventory {self.item_name}: {self.quantity}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(200), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Dispatched")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track when order was created
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Track status updates
    
    def __repr__(self):
        return f'<Order #{self.id}: {self.item_name} to {self.hospital_name}>'