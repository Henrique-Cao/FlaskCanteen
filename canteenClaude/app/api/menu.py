from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import MenuItem

menu_api = Blueprint('menu_api', __name__)

@menu_api.route('/', methods=['GET'])
def get_all_items():
    items = MenuItem.query.all()
    # Serialize Python objects into JSON-compatible lists/dictionaries
    serialized_items = [
        {
            "id": item.id,
            "name": item.name,
            "price": float(item.price),
            "is_available": item.is_available
        } for item in items
    ]
    return jsonify(serialized_items), 200

@menu_api.route('/', methods=['POST'])
def add_menu_item():
    # 1. Extract the raw JSON data sent from the frontend
    data = request.get_json() or {}
    
    # 2. Simple validation: Ensure required fields are present
    if 'name' not in data or 'price' not in data:
        return jsonify({"error": "Missing required fields: 'name' and 'price' are mandatory."}), 400
        
    try:
        # 3. Create a new instance of the database model
        new_item = MenuItem(
            name=data['name'],
            price=float(data['price']),
            description=data.get('description', ""),
            # FIX: Pull category from incoming JSON, or default to "Mains"
            category=data.get('category', "Mains"), 
            image_filename=data.get('image_filename', "placeholder.jpg"),
            is_available=data.get('is_available', True) 
        )
        
        # 4. Save to SQLite database
        db.session.add(new_item)
        db.session.commit()
        
        # 5. Return a success response along with the newly created item ID
        return jsonify({
            "message": "Item added successfully!",
            "item_id": new_item.id
        }), 201

    except ValueError:
        return jsonify({"error": "Invalid data format. Price must be a number."}), 400
    except Exception as e:
        db.session.rollback()  # Rollback changes if something breaks
        return jsonify({"error": f"Internal database error: {str(e)}"}), 500
    
@menu_api.route('/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    try:
        # 1. Look for the item by its ID
        item = MenuItem.query.get(item_id)
        
        # 2. If the item doesn't exist, return a 404 error
        if not item:
            return jsonify({"error": f"Menu item with ID {item_id} not found."}), 404
            
        # 3. Remove the item from the session and commit changes
        db.session.delete(item)
        db.session.commit()
        
        # 4. Return a success message
        return jsonify({
            "message": f"Item '{item.name}' (ID: {item_id}) has been successfully deleted."
        }), 200

    except Exception as e:
        db.session.rollback()  # Safely roll back the transaction on error
        return jsonify({"error": f"Internal database error: {str(e)}"}), 500