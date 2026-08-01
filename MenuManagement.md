# Technical Documentation: Admin Menu & Category Management

## 1. Overview
The Admin Menu & Category Management system is designed as a responsive, asynchronous management dashboard for the canteen ordering web app. It transitions traditional full-page form reloads (`POST` + redirect) into a modern, dynamic single-page experience using standard **Flask (Python)** backend routes, **Flask-SQLAlchemy** ORM, and client-side **Fetch API** calls with **SortableJS**.

---

## 2. Database Architecture (`models.py`)

The data model uses a One-to-Many relational structure between `Category` and `MenuItem`, configured with **Nullable Foreign Keys** to support optional categories and safe deletion semantics.


### ------Insert Database Modal chart here------


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








