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

@menu_api.route('/<int:item_id>', methods=['GET'])
def get_menu_item_details(item_id):
    # Returns raw item data to build forms asynchronously
    item = MenuItem.query.get_or_404(item_id)
    return jsonify({
        'id': item.id,  
        'name': item.name,
        'description': item.description,
        'price': float(item.price),
        'category_id': item.category_id,
        'category_name': item.category.name if item.category else None,
        'image_filename': item.image_filename,
        'is_available': item.is_available
    })

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
            category_id = data.get('category', None),  # Use None if no category is provided
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
    
@menu_api.route('/update/<int:item_id>', methods=['POST'])
def update_menu_item(item_id):
    # 1. Locate the target item row or return an error clean log if missing

    item = MenuItem.query.get_or_404(item_id)
    
    # 2. Extract the incoming JSON payload bundle sent from your script
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data payload received'}), 400

    try:
        # 3. Map values from the payload into your database model instance attributes
        item.name = data.get('name', item.name)
        item.category_id = data.get('category', item.category_id)
        item.description = data.get('description', item.description)
        
        # Explicit type conversion prevents string comparison crashes in SQL engine
        if 'price' in data:
            item.price = float(data['price'])   

        

        # 4. Commit updates directly down to your SQLite file records
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Item #{item_id} synchronized successfully.'})

    except Exception as e:
        db.session.rollback()
        print(f"Database update execution tracking failed: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal database exception encountered'}), 500