# Customer and staff guide

## For customers

1. Open the home page and browse the menu.
2. Add items to the cart. The cart is associated with the current browser session.
3. Submit the order with a customer name and phone number.
4. Keep the order number from the confirmation page. Use the tracking page to look up an order by order number or phone number.

The application records orders and supports status tracking. It does not include an online payment flow.

## For staff

Sign in with an administrator account provisioned for the environment. The admin pages are available under `/admin/`.

- **Dashboard:** view order and sales metrics, including date-range views.
- **Manage menu:** create or edit menu items, upload an image, change availability, and organize categories. See [Menu management](MenuManagement.md).
- **Orders:** review orders and update their status.
- **History:** search and filter completed orders by customer/order details, status, date, and total.

Order statuses stored by the application are `pending`, `confirmed`, `ready`, `completed`, and `cancelled`. The supported status controls and what each transition means operationally should be confirmed with the canteen team before using the app for live service.

## Getting an administrator account

Users are stored in the `users` table. The repository does not provide a safe production account-provisioning workflow. `seeddb.py` is destructive and intended only for disposable development data; do not use it to create a live administrator account. Provision administrator credentials through an approved, controlled process.

## Current limitations

- No payment processing or customer notification integration is included.
- Staff sign-in checks protect the admin page blueprint, but the JSON API does not consistently enforce admin authorization. See [Configuration and deployment](configuration-and-deployment.md) before exposing the app.
- Some older cart/order routes are incomplete; use the working flows described here and the [API reference](api-reference.md).
