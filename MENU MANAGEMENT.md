# Technical Documentation: Admin Menu & Category Management

## 1. Overview
The Admin Menu & Category Management system is designed as a responsive, asynchronous management dashboard for the canteen ordering web app. It transitions traditional full-page form reloads (`POST` + redirect) into a modern, dynamic single-page experience using standard **Flask (Python)** backend routes, **Flask-SQLAlchemy** ORM, and client-side **Fetch API** calls with **SortableJS**.

---

## 2. Database Architecture (`models.py`)

The data model uses a One-to-Many relational structure between `Category` and `MenuItem`, configured with **Nullable Foreign Keys** to support optional categories and safe deletion semantics.

```
+--------------------+            +-----------------------+
|     Category       |            |       MenuItem        |
+--------------------+            +-----------------------+
| id (PK, Integer)   | 1       *  | id (PK, Integer)      |
| name (String)      |------------| name (String)         |
| position (Integer) |            | price (Numeric)       |
+--------------------+            | description (Text)    |
                                  | image_filename (Str)  |
                                  | is_available (Bool)   |
                                  | category_id (FK, Null)|
                                  +-----------------------+
```

### Schema Rules & Design Choices
1. **Nullable Category Linkage (`category_id` = `NULL`)**:
   * Menu items do not strictly require a category. If unassigned, `category_id` is set to `None` (SQL `NULL`).
   * Unassigned items are automatically assigned to an `"Uncategorized"` view group in the frontend.
2. **Safe Deletion Policy**:
   * Deleting a category **does not** delete its associated menu items (`cascade="all, delete-orphan"` is intentionally omitted).
   * Before a category record is removed, all associated menu items are unlinked (`category_id = None`), transferring them gracefully into the `"Uncategorized"` group.
3. **JSON Serialization Method (`to_dict`)**:
   * SQLAlchemy models include a helper method (`to_dict()`) to prevent `TypeError: Object of type Category/MenuItem is not JSON serializable` errors when returning responses via `jsonify()`.

---

## 3. Backend Implementation (Flask API)

### A. Data Sanitization Pattern
When instantiating or updating a `MenuItem`, incoming category data (`raw_category`, `category_id`, or `category`) is processed before passing it to the SQLAlchemy constructor:

```python
# Extract raw category input safely
raw_category = data.get('category') or data.get('raw_category') or data.get('category_id')

category_id = None
if raw_category is not None:
    raw_str = str(raw_category).strip()
    if raw_str:
        category_id = int(raw_str)

new_item = MenuItem(
    name=data['name'],
    price=float(data['price']),
    description=data.get('description', ""),
    category_id=category_id, # Stores int or None
    image_filename=data.get('image_filename', "placeholder.jpg"),
    is_available=data.get('is_available', True)
)
```

### B. Category Deletion Route
```python
@admin_bp.route('/admin/category/delete/<int:category_id>', methods=['POST', 'DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    try:
        # Unlink associated items prior to deletion
        for item in category.items:
            item.category_id = None

        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category deleted. Items moved to Uncategorized.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
```

---

## 4. Frontend Architecture & Drag-and-Drop (`admin_menu.js`)

### A. Drag-and-Drop Reordering (SortableJS)
Category reordering relies on exact class contract alignment between Jinja2 HTML templates and JavaScript.

#### Class Contract Alignment:
| Component | Class Name | Function |
| :--- | :--- | :--- |
| **Container** | `#categoryList` | Root list element initialized by SortableJS. |
| **Item Row** | `.dragItem` | Individual category item container. |
| **Grip Handle** | `.dragHandle` | Grab icon targeted by `handle: '.dragHandle'`. |
| **Position Badge** | `.badgePos` | Numerical badge updated on drop (`index0`). |

#### JavaScript Initialization & Order Sync:
```javascript
function initSortable() {
    const container = document.getElementById('categoryList');
    if (!container) return;

    const sortable = new Sortable(container, {
        animation: 200,
        handle: '.dragHandle',
        onEnd: function () {
            const orderedIds = sortable.toArray().map(id => parseInt(id, 10));

            // Update position badges in real time
            container.querySelectorAll('.dragItem').forEach((item, index) => {
                const posBadge = item.querySelector('.badgePos');
                if (posBadge) posBadge.textContent = index;
            });

            saveNewOrder(orderedIds);
        }
    });
}

async function saveNewOrder(orderedIds) {
    try {
        await fetchJSON('/api/categories/reorder', {
            method: 'POST',
            body: JSON.stringify({ ordered_ids: orderedIds })
        });
    } catch (error) {
        console.error('Error updating order:', error);
        alert("Failed to save category order.");
    }
}
```

### B. Asynchronous Form Submissions & Event Delegation
* **No Page Reloads**: Forms intercept the default submit event (`e.preventDefault()`) and transmit payload via `fetchJSON()`.
* **Dynamic Rendering**: Upon receiving a `{ success: true, item: {...} }` response, helper functions construct DOM nodes dynamically and append/update the view.
* **Event Delegation**: Action buttons (like edit/delete) inside dynamically rendered DOM items use delegated event listeners attached to parent containers (`#categoryList` or `#menuItemsContainer`).

---

## 5. Summary of Resolved Pitfalls

1. **`TypeError: Object of type Category is not JSON serializable`**:
   * *Root Cause*: Attempting to pass raw SQLAlchemy model instances into `jsonify()`.
   * *Resolution*: Serializing models to dictionaries explicitly (`item.category.name if item.category else 'Uncategorized'` or using `.to_dict()`).
2. **`TypeError: 'int' object has no attribute '_sa_instance_state'`**:
   * *Root Cause*: Passing integer values to SQLAlchemy relationship properties (`category=1`) instead of foreign key columns (`category_id=1`).
   * *Resolution*: Standardized model instantiation to assign integer IDs strictly to `category_id`.
3. **Broken Drag-and-Drop Handle**:
   * *Root Cause*: Mismatched class names between JS selector `.dragHandle` and Jinja HTML `class="drag-handle"`.
   * *Resolution*: Standardized class names across HTML templates and JS selectors.

---

## 6. Image Upload & File Handling Pipeline

Menu items support image uploads with fallback handling for unassigned or missing images.

### Upload Logic (`routes.py` / `utils.py`)
* Images are uploaded via `multipart/form-data`.
* Unique filenames are generated using `uuid` to prevent filename collisions.
* Saved to `static/uploads/menu_items/`.

```python
import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def save_menu_image(file):
    if not file or file.filename == '':
        return "placeholder.jpg"

    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    
    return "placeholder.jpg"
```

---

## 7. API Endpoint Reference

| Endpoint | Method | Payload / Params | Description | Response |
| :--- | :--- | :--- | :--- | :--- |
| `/api/categories/reorder` | `POST` | `{ "ordered_ids": [3, 1, 2] }` | Updates category sorting positions. | `{ "success": true }` |
| `/admin/category/add` | `POST` | `FormData(name)` | Creates a new category. | `{ "success": true, "category": {...} }` |
| `/admin/category/delete/<id>` | `DELETE` | `None` | Deletes category and unlinks items. | `{ "success": true, "message": "..." }` |
| `/menu/item/<id>` | `GET` | `None` | Fetches item details for edit modal. | `{ "success": true, "item": {...} }` |
| `/admin/menu/add` | `POST` | `FormData(...)` | Adds a new menu item. | `{ "success": true, "item": {...} }` |
| `/admin/menu/edit/<id>` | `POST` | `FormData(...)` | Updates existing menu item. | `{ "success": true, "item": {...} }` |

---

## 8. Dynamic DOM Helpers (`admin_menu.js`)

To update the UI without reloading the page, the client uses dedicated DOM builder functions:

```javascript
/**
 * Appends or updates a menu item card inside its designated category section.
 */
function updateMenuItemDOM(item) {
    const categoryTargetId = item.category_id ? `cat-group-${item.category_id}` : 'cat-group-uncategorized';
    const container = document.getElementById(categoryTargetId);

    if (!container) return;

    let existingCard = document.querySelector(`[data-item-id="${item.id}"]`);

    const cardHTML = `
        <div class="card-body d-flex justify-content-between align-items-center">
            <div>
                <h6 class="mb-0 fw-bold">${item.name}</h6>                 <small class="text-muted">$${item.price.toFixed(2)}</small>
            </div>
            <div class="btn-group">
                <button class="btn btn-sm btn-outline-secondary" onclick="openEditModal(${item.id})">Edit</button>
            </div>
        </div>
    `;

    if (existingCard) {
        existingCard.innerHTML = cardHTML;
    } else {
        const newCard = document.createElement('div');
        newCard.className = 'card mb-2 item-card';
        newCard.setAttribute('data-item-id', item.id);
        newCard.innerHTML = cardHTML;
        container.appendChild(newCard);
    }
}
```

---

## 9. Local Setup & Database Initialization

1. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   flask db init
   flask db migrate -m "Initial menu and category schema"
   flask db upgrade
   ```

3. **Run Application**:
   ```bash
   flask run
   ```





