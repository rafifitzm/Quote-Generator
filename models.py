# User and Quote models
from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))  # Hash passwords in prod

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String(150))
    service = db.Column(db.String(150))
    price = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # By default, SQLAlchemy generates the table
    # name by converting the class name to lowercase.
