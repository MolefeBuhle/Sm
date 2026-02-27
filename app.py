from flask import Flask, render_template, request, redirect, flash
from config import Config
from models import db, Inventory, Order, User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------------
# USER LOADER
# ---------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------
# CREATE DATABASE
# ---------------------
with app.app_context():
    db.create_all()

# ---------------------
# REGISTER
# ---------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect("/register")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect("/login")

    return render_template("register.html")

# ---------------------
# LOGIN
# ---------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html")

# ---------------------
# LOGOUT
# ---------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# ---------------------
# DASHBOARD
# ---------------------
@app.route("/")
@login_required
def dashboard():
    inventory_count = Inventory.query.count()
    order_count = Order.query.count()
    return render_template("dashboard.html",
                           inventory_count=inventory_count,
                           order_count=order_count)

# ---------------------
# INVENTORY
# ---------------------
@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    if request.method == "POST":
        item_name = request.form["item_name"]
        quantity = int(request.form["quantity"])

        existing_item = Inventory.query.filter_by(item_name=item_name).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = Inventory(item_name=item_name, quantity=quantity)
            db.session.add(new_item)

        db.session.commit()
        return redirect("/inventory")

    items = Inventory.query.all()
    return render_template("inventory.html", items=items)

# ---------------------
# ORDERS
# ---------------------
@app.route("/orders", methods=["GET", "POST"])
@login_required
def orders():
    if request.method == "POST":
        hospital_name = request.form["hospital_name"]
        item_name = request.form["item_name"]
        quantity = int(request.form["quantity"])

        inventory_item = Inventory.query.filter_by(item_name=item_name).first()

        if not inventory_item:
            flash("Item does not exist in inventory.", "danger")
            return redirect("/orders")

        if inventory_item.quantity < quantity:
            flash("Insufficient stock available.", "danger")
            return redirect("/orders")

        inventory_item.quantity -= quantity

        new_order = Order(
            hospital_name=hospital_name,
            item_name=item_name,
            quantity=quantity,
            status="Dispatched"
        )

        db.session.add(new_order)
        db.session.commit()

        flash("Order created successfully!", "success")
        return redirect("/orders")

    orders = Order.query.all()
    return render_template("orders.html", orders=orders)

if __name__ == "__main__":
    app.run(debug=True)
