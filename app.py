from flask import Flask, render_template, request, redirect, flash, url_for
from config import Config
from models import db, Inventory, Order, User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Verify secret key is set properly
if app.config['SECRET_KEY'] == 'dev-key-change-in-production':
    logger.warning("Using default secret key - this is insecure for production!")

# Session configuration for production
app.config['SESSION_COOKIE_SECURE'] = True  # Required for HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.session_protection = "strong"

# ---------------------
# USER LOADER
# ---------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------
# CREATE DATABASE AND DEFAULT ADMIN
# ---------------------
with app.app_context():
    logger.info("Creating database tables...")
    db.create_all()
    
    # Check if any users exist
    if User.query.count() == 0:
        logger.info("No users found. Creating default admin user...")
        admin = User(
            username="admin", 
            password=generate_password_hash("admin")
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created: username='admin', password='admin'")
    else:
        logger.info(f"Found {User.query.count()} existing users.")

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
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------------
# LOGIN
# ---------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        logger.info(f"Login attempt for user: {username}")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            logger.info(f"Login successful for user: {username}")
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            logger.warning(f"Login failed for user: {username}")
            flash("Invalid credentials.", "danger")

    return render_template("login.html")

# ---------------------
# LOGOUT
# ---------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

# ---------------------
# DASHBOARD
# ---------------------
@app.route("/")
@login_required
def dashboard():
    inventory_count = Inventory.query.count()
    order_count = Order.query.count()
    logger.info(f"Dashboard accessed by user: {current_user.username}")
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
            flash(f"Updated {item_name} quantity to {existing_item.quantity}", "success")
        else:
            new_item = Inventory(item_name=item_name, quantity=quantity)
            db.session.add(new_item)
            flash(f"Added new item: {item_name}", "success")

        db.session.commit()
        return redirect(url_for("inventory"))

    items = Inventory.query.all()
    return render_template("inventory.html", items=items)

# ---------------------
# DELETE INVENTORY ITEM
# ---------------------
@app.route("/inventory/delete/<int:item_id>")
@login_required
def delete_inventory(item_id):
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"Deleted {item.item_name} from inventory", "success")
    return redirect(url_for("inventory"))

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
            return redirect(url_for("orders"))

        if inventory_item.quantity < quantity:
            flash(f"Insufficient stock. Available: {inventory_item.quantity}", "danger")
            return redirect(url_for("orders"))

        inventory_item.quantity -= quantity

        new_order = Order(
            hospital_name=hospital_name,
            item_name=item_name,
            quantity=quantity,
            status="Dispatched"
        )

        db.session.add(new_order)
        db.session.commit()

        flash(f"Order created successfully for {hospital_name}!", "success")
        return redirect(url_for("orders"))

    orders = Order.query.all()
    inventory_items = Inventory.query.all()
    return render_template("orders.html", orders=orders, inventory_items=inventory_items)

# ---------------------
# UPDATE ORDER STATUS
# ---------------------
@app.route("/orders/update/<int:order_id>")
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == "Dispatched":
        order.status = "Delivered"
        flash(f"Order #{order_id} marked as delivered", "success")
    else:
        order.status = "Dispatched"
        flash(f"Order #{order_id} marked as dispatched", "success")
    
    db.session.commit()
    return redirect(url_for("orders"))

# ---------------------
# HEALTH CHECK (for Render)
# ---------------------
@app.route("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "users": User.query.count(),
        "inventory": Inventory.query.count(),
        "orders": Order.query.count()
    }, 200

# ---------------------
# ERROR HANDLERS
# ---------------------
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback any failed transactions
    logger.error(f"500 error: {error}")
    return render_template("500.html"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)