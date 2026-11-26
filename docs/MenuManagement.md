# Manage menu items and categories

This guide covers the staff menu-management page at `/admin/manage-menu`.

## Menu items

Use the menu-management page to review existing items and add, edit, or remove them. An item has a name, price, optional description, optional category, availability flag, and image filename.

When adding an image, the page submits it as multipart form data. The server generates a filename, normalizes the image, scales it to fit within 600 × 600 pixels, and stores it in `canteenClaude/app/static/uploads/`. The database stores the generated filename.

Use the availability control to update the item's stored availability flag without deleting its record. The current customer menu templates do not filter on that flag, so verify customer-visible behavior before relying on the control to hide an item. Deleting an item is a permanent database action and may affect the display of historical order lines.

## Categories

Categories are shown in their configured display order. Staff can create, rename, delete, and reorder categories. Items may have no category; the staff menu groups those items under “Uncategorized”.

Reordering is saved through `POST /api/categories/reorder` with an `ordered_ids` array:

```json
{
  "ordered_ids": [3, 1, 2]
}
```

The full route list and the remaining request formats are in the [API reference](api-reference.md).

## Implementation notes for contributors

- The page is rendered by `app/admin/routes.py` and `app/templates/admin/manage_menu.html`.
- Menu and category mutations are implemented in `app/api/menu.py` and `app/api/categories.py`.
- Uploaded images use the `UPLOAD_FOLDER` application setting.
- Update the relevant route/API docs and add focused tests when changing a form field, response, or persistence behavior.

The JSON write endpoints currently do not all enforce admin authorization. Do not treat access to this page as proof that the corresponding API operations are protected; see [Configuration and deployment](configuration-and-deployment.md).
