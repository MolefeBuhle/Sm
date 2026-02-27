from flask import Blueprint, request, redirect, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = generate_password_hash(request.form["password"])

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return "User Registered"

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        return "Login Successful"

    return "Invalid Credentials"
