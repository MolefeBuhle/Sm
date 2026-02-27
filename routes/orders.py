from flask import Blueprint, request, jsonify
from models import Order
from app import db

orders_bp = Blueprint("orders", __name__)

# CREATE ORDER
@orders_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.json

    order = Order(
        hospital_name=data["hospital_name"],
        item_name=data["item_name"],
        quantity=data["quantity"]
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Order created"})

# READ ORDERS
@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()

    output = []
    for order in orders:
        output.append({
            "id": order.id,
            "hospital_name": order.hospital_name,
            "item_name": order.item_name,
            "quantity": order.quantity,
            "status": order.status
        })

    return jsonify(output)

# UPDATE STATUS
@orders_bp.route("/orders/<int:id>", methods=["PUT"])
def update_order(id):
    order = Order.query.get_or_404(id)
    data = request.json

    order.status = data["status"]
    db.session.commit()

    return jsonify({"message": "Order updated"})
