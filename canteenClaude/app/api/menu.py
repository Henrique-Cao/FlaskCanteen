import os
import uuid

from flask import Blueprint, app, current_app, jsonify, request, url_for, flash, redirect
from app.extensions import db
from app.models import MenuItem
from PIL import Image, ImageOps

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
    
    # # 1. Extract the raw JSON data sent from the frontend
    # data = request.get_json() or {}
    # print(data)
    # # 2. Simple validation: Ensure required fields are present
    # if 'name' not in data or 'price' not in data:
    #     return jsonify({"error": "Missing required fields: 'name' and 'price' are mandatory."}), 400

    # Because we used FormData in JS, we read text like this:
    name = request.form.get('addName')
    category_id = request.form.get('addCategory')
    price = request.form.get('addPrice')
    description = request.form.get('addDescription')
    try:
        
        # 3. Create a new instance of the database model
        
        if 'image' in request.files:
            file = request.files['image']
        
            if file and file.filename != '':
                
                # 1. Generate a completely secure, random filename
                extension = file.filename.rsplit('.', 1)[1].lower()
                secure_name = f"{uuid.uuid4().hex}.{extension}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_name)
                
                try:
                    # 2. Open the image in memory using Pillow
                    img = Image.open(file)
                    
                    # 3. Strip EXIF data (fixes rotation issues from iPhone photos)
                    img = ImageOps.exif_transpose(img)
                    
                    # 4. Convert to RGB (prevents errors if user uploads a transparent PNG but saves as JPG)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 5. Crop and resize to a perfect, fast-loading 600x600 square
                    # Image.Resampling.LANCZOS maintains the highest visual quality during resizing
                    img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                    
                    # 6. Save to disk with aggressive web compression (quality=85)
                    img.save(filepath, optimize=True, quality=85)
                    
                    # 7. Set the variable to save to SQLite
                    saved_filename = secure_name
                    
                except Exception as e:
                    print("image processing failed")
                    flash(f"Image processing failed: {str(e)}")
                    return redirect(url_for('admin.manage_menu'))
        
        new_item = MenuItem(
                    name=name,
                    price=price,
                    description=description,
                    category_id = category_id,  # Use None if no category is provided
                    is_available=True,
                    image_filename=saved_filename
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


@menu_api.route('/update/<int:item_id>', methods=['POST'])
def update_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.name = request.form.get('editName')
    item.price = request.form.get('editPrice')
    item.category_id = request.form.get('editCategory')
    item.description = request.form.get('editDescription')
    saved_filename = 'placeholder.jpg'
    try:
        if 'editImage' in request.files:
            file = request.files['editImage']
            print(file)
            if file and file.filename != '':
                
                # 1. Generate a completely secure, random filename
                extension = file.filename.rsplit('.', 1)[1].lower()
                secure_name = f"{uuid.uuid4().hex}.{extension}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_name)
                
                try:
                    # 2. Open the image in memory using Pillow
                    img = Image.open(file)
                    
                    # 3. Strip EXIF data (fixes rotation issues from iPhone photos)
                    img = ImageOps.exif_transpose(img)
                    
                    # 4. Convert to RGB (prevents errors if user uploads a transparent PNG but saves as JPG)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 5. Crop and resize to a perfect, fast-loading 600x600 square
                    # Image.Resampling.LANCZOS maintains the highest visual quality during resizing
                    img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                    
                    # 6. Save to disk with aggressive web compression (quality=85)
                    img.save(filepath, optimize=True, quality=85)
                    
                    # 7. Set the variable to save to SQLite
                    saved_filename = secure_name
                    print(saved_filename    )
                except Exception as e:
                    print("image processing failed")
                    flash(f"Image processing failed: {str(e)}")
                    return redirect(url_for('admin.manage_menu'))
        print("here")
        
        item.image_filename = saved_filename
        db.session.commit()
        
        return jsonify({
                    "message": "Item updated successfully!",
                    "item_id": item.id
                }), 200
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

        imagefile = item.image_filename
        if imagefile and imagefile != 'placeholder.jpg':
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], imagefile))
        
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





# @menu_api.route('/update/<int:item_id>', methods=['POST'])
# def update_menu_item(item_id):
#     # 1. Locate the target item row or return an error clean log if missing

#     item = MenuItem.query.get_or_404(item_id)
    
#     # 2. Extract the incoming JSON payload bundle sent from your script
#     data = request.get_json()
#     if not data:
#         return jsonify({'status': 'error', 'message': 'No data payload received'}), 400

#     try:
#         # 3. Map values from the payload into your database model instance attributes
#         item.name = data.get('name', item.name)
#         item.category_id = data.get('category', item.category_id)
#         item.description = data.get('description', item.description)
        
#         # Explicit type conversion prevents string comparison crashes in SQL engine
#         if 'price' in data:
#             item.price = float(data['price'])   

        

#         # 4. Commit updates directly down to your SQLite file records
#         db.session.commit()
#         return jsonify({'status': 'success', 'message': f'Item #{item_id} synchronized successfully.'})

#     except Exception as e:
#         db.session.rollback()
#         print(f"Database update execution tracking failed: {str(e)}")
#         return jsonify({'status': 'error', 'message': 'Internal database exception encountered'}), 500

@menu_api.route('/toggle/<int:item_id>/<checked>', methods=['POST'])
def toggle_menu_item_visibility(item_id, checked):
    print(f"Toggling visibility for item_id={item_id} to checked={checked}")
    try:
        item = MenuItem.query.get_or_404(item_id)
        item.is_available = checked.lower() == 'true'
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Item #{item_id} visibility toggled successfully.', 'is_available': item.is_available})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Internal database exception encountered: {str(e)}'}), 500