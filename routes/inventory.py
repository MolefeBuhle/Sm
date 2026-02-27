from flask import Blueprint, request, jsonify
from models import Inventory
from app import db

inventory_bp = Blueprint("inventory", __name__)

# CREATE
@inventory_bp.route("/inventory", methods=["POST"])
def add_item():
    data = request.json

    item = Inventory(
        item_name=data["item_name"],
        quantity=data["quantity"]
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({"message": "Item added successfully"})

# READ
@inventory_bp.route("/inventory", methods=["GET"])
def get_items():
    items = Inventory.query.all()

    output = []
    for item in items:
        output.append({
            "id": item.id,
            "item_name": item.item_name,
            "quantity": item.quantity
        })

    return jsonify(output)

# UPDATE
@inventory_bp.route("/inventory/<int:id>", methods=["PUT"])
def update_item(id):
    item = Inventory.query.get_or_404(id)
    data = request.json

    item.quantity = data["quantity"]
    db.session.commit()

    return jsonify({"message": "Item updated"})

# DELETE
@inventory_bp.route("/inventory/<int:id>", methods=["DELETE"])
def delete_item(id):
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item deleted"})
@inventory_bp.route("/inventory/search", methods=["GET"])
def search_item():
    name = request.args.get("name")
    items = Inventory.query.filter(Inventory.item_name.contains(name)).all()

    return jsonify([
        {"id": i.id, "item_name": i.item_name, "quantity": i.quantity}
        for i in items
    ])
