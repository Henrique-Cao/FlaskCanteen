# Readability and Maintainability Audit — Refactoring Plan

## Scope and guardrails

- Reviewed project Python/Flask source, Jinja templates, SCSS/CSS, and JavaScript. Excluded the virtual environment, local SQLite database, and binary image assets from readability findings.
- Batch 1 (debug/dead-code hygiene) was executed after approval. No later refactoring batches have been started.
- All legacy/versioned assets below are *candidates* until route, template, static-asset, and deployment references are verified. No route, file, selector, or API contract should be removed based only on its name.
- Preserve current response data, status semantics, form field names, Jinja context variables, endpoint names, layout, and dynamic styles. Keep small, clear inline logic inline.

## 1. Debug & Dead Code

### 1.1 Remove or gate development logging
- **Location:** Active backend calls in [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L176), [`app/main/routes.py`](../../../Documents/Proj/canteenClaude/app/main/routes.py#L56), [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L42), [`app/cart/routes.py`](../../../Documents/Proj/canteenClaude/app/cart/routes.py#L35), [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L92), [`app/api/categories.py`](../../../Documents/Proj/canteenClaude/app/api/categories.py#L23), [`app/api/cart.py`](../../../Documents/Proj/canteenClaude/app/api/cart.py#L39), and [`app/api/authentication.py`](../../../Documents/Proj/canteenClaude/app/api/authentication.py#L40). Client-side logging also appears in [`app/static/js/pages/admin_menu.js`](../../../Documents/Proj/canteenClaude/app/static/js/pages/admin_menu.js#L77), [`app/static/js/admin.js`](../../../Documents/Proj/canteenClaude/app/static/js/admin.js#L7), [`app/static/js/main.js`](../../../Documents/Proj/canteenClaude/app/static/js/main.js#L34), [`app/static/js/features/forms.js`](../../../Documents/Proj/canteenClaude/app/static/js/features/forms.js#L19), and cart/order scripts.
- **Current Issue:** Console output includes request/order/cart state and status messages that appear to be development tracing rather than operational diagnostics.
- **Proposed Change:** Remove transient `print()`/`console.log()` calls, or replace only actionable failures with the project’s chosen logger. Retain intentional progress output in database seed/clear scripts unless those are also being converted to CLI logging.
- **Why It Helps:** Keeps normal server/browser output useful and avoids noise in routine workflows.
- **Risk / Cross-File Dependencies:** **Low.** No route, template, form, payload, or selector dependency; retain meaningful error reporting.

### 1.2 Remove unreachable statements and stale commented blocks
- **Location:** [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L57) returns when `order` is truthy, making the later second `if order` block at lines 62–63 unreachable. [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L143) has a duplicate return at line 145. Large commented alternatives remain in `admin/routes.py` around lines 52–63, `order_confirmation/routes.py` around lines 127–142, [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L218), [`app/api/analytics.py`](../../../Documents/Proj/canteenClaude/app/api/analytics.py#L180), and [`app/templates/menu/menu.html`](../../../Documents/Proj/canteenClaude/app/templates/menu/menu.html#L160).
- **Current Issue:** Dead paths and obsolete implementations compete with the current flow and obscure the behavior that actually runs.
- **Proposed Change:** Delete unreachable statements and remove obsolete commented code after confirming no intended behavior is lost; keep design/history explanations in documentation only when still useful.
- **Why It Helps:** Makes control flow and the supported implementation unambiguous.
- **Risk / Cross-File Dependencies:** **Low–Medium.** The stale blocks refer to older template context and API payloads; do not remove or rename the live `main.confirmation`, `order_confirmation.index`, or menu API endpoints while cleaning comments.

### 1.3 Treat versioned/unreferenced modules and assets as deletion candidates, not proven dead code
- **Location:** The factory registers blueprints from [`app/__init__.py`](../../../Documents/Proj/canteenClaude/app/__init__.py#L56), while [`app/menu/routes.py`](../../../Documents/Proj/canteenClaude/app/menu/routes.py#L3) and [`app/orders/routes.py`](../../../Documents/Proj/canteenClaude/app/orders/routes.py#L3) are not registered there; [`app/api/orders.py`](../../../Documents/Proj/canteenClaude/app/api/orders.py) is empty. In-repository render/include/static references do not show active use for candidates including `templates/base2.html`, `base3.html`, `admin_base2.html`, numbered `main/index*`, `menu/menu2.html`, numbered admin/history/order-confirmation templates, `partials/_filter_dropdown1.html`, `services/analytics_service1.py`, and legacy JS/SCSS variants such as `admin_menu2.js`, `admin_menu3.js`, `_variables1/2/3.scss`, and `main..scss`.
- **Current Issue:** Numeric suffixes and parallel entrypoints make it difficult to tell supported assets from abandoned alternatives; a repository search alone cannot rule out deployment scripts or external consumers.
- **Proposed Change:** Build a single route → template → static asset reference map. Remove only files confirmed unused by application startup, tests, build/deployment configuration, and any documented external use. Keep the active path (`main/index.html`, `admin_base.html`, `admin/*.html`, `scss/main.css`, and the imported `pages/*.js` modules) intact.
- **Why It Helps:** Reduces navigation overhead and prevents accidental edits to stale variants.
- **Risk / Cross-File Dependencies:** **High before verification; Low after verification.** Check all `render_template()`, Jinja `{% extends/include %}`, `url_for('static', ...)`, Sass imports, JS imports, and direct URL consumers. Legacy templates currently point at old scripts/styles; remove those references with their templates, not independently.

### 1.4 Resolve unfinished checkout call paths before labeling them dead
- **Location:** [`app/cart/routes.py`](../../../Documents/Proj/canteenClaude/app/cart/routes.py#L38) calls `cart_service.get_cart_items()` and `cart_service.clear_cart()`, which are not defined in [`app/services/cart_service.py`](../../../Documents/Proj/canteenClaude/app/services/cart_service.py). [`app/api/order.py`](../../../Documents/Proj/canteenClaude/app/api/order.py#L100) imports `create_order_from_cart`, absent from [`app/services/order_service.py`](../../../Documents/Proj/canteenClaude/app/services/order_service.py).
- **Current Issue:** Two exposed checkout implementations appear incomplete and may fail if called; it is unclear whether they are abandoned or expected API paths.
- **Proposed Change:** Trace callers and expected checkout contracts first. Then either remove the unused route(s) with explicit endpoint/client verification, or implement the missing service operations as a separately approved behavior-preserving change.
- **Why It Helps:** Prevents incomplete code from being mistaken for a supported checkout path.
- **Risk / Cross-File Dependencies:** **High.** Verify `cart.checkout`, checkout form action/HTMX target, `/api/order/create`, cart session schema, `create_order()` API payload, and confirmation redirects before changing anything.

## 2. Unclear Naming

### 2.1 Replace numeric-version naming on the active analytics service
- **Location:** [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L8) imports both `get_dashboard_metrics` and `get_dashboard_metrics2`; the active handler calls `get_dashboard_metrics2` into `metrics2` at line 51. The implementation is in [`app/services/analytics_service2.py`](../../../Documents/Proj/canteenClaude/app/services/analytics_service2.py#L213); the unnumbered/`1` siblings are not the active handler’s implementation.
- **Current Issue:** `2` suffixes do not describe the selected implementation, while the older import and commented call suggest competing versions.
- **Proposed Change:** After confirming which analytics implementation is canonical, give the service/module and local variable descriptive stable names and remove the unused import. Do not rename the service until deciding what to do with the older module.
- **Why It Helps:** Readers can identify the supported implementation without reconstructing version history.
- **Risk / Cross-File Dependencies:** **Medium.** Update the import/call in `admin/routes.py` and tests/imports. Preserve the `metrics` dictionary keys passed to `partials/_analytics_content.html` (`kpi`, `chart_labels`, `chart_revenue`, `chart_traffic`, top item/category values, and `meta`) and the current `admin.analytics_content` endpoint.

### 2.2 Rename helpers whose names overstate or obscure their behavior
- **Location:** [`app/services/order_service.py`](../../../Documents/Proj/canteenClaude/app/services/order_service.py#L76) `get_order_by_numeric_input()` normalizes a submitted value and returns an order-number string; it does not query the database. [`app/api/order.py`](../../../Documents/Proj/canteenClaude/app/api/order.py#L101) names a second handler `create_order2()`.
- **Current Issue:** Names imply database lookup and a meaningful second order-creation variant, respectively.
- **Proposed Change:** Rename the normalization helper to a name such as `normalize_order_number`; only rename or remove `create_order2` after resolving the unfinished checkout path in finding 1.4.
- **Why It Helps:** The function names communicate actual responsibility and discourage callers from assuming a lookup occurred.
- **Risk / Cross-File Dependencies:** **Low** for the helper rename: update its import/call in `main/routes.py` only. Keep the `/track_order` route, `name="order_number"` form field, `main.confirmation` endpoint, and returned order-number format unchanged. **High** for `create_order2` until callers are verified.

### 2.3 Standardize the few mixed-case CSS/HTML hooks with synchronized edits
- **Location:** `dragHandle` in [`app/templates/admin/manage_menu.html`](../../../Documents/Proj/canteenClaude/app/templates/admin/manage_menu.html#L46) is selected by `handleClass: '.dragHandle'` in [`app/static/js/pages/admin_menu.js`](../../../Documents/Proj/canteenClaude/app/static/js/pages/admin_menu.js#L138) and passed to [`app/static/js/features/dragDrop.js`](../../../Documents/Proj/canteenClaude/app/static/js/features/dragDrop.js#L6). [`app/templates/order_confirmation/order_confirmation.html`](../../../Documents/Proj/canteenClaude/app/templates/order_confirmation/order_confirmation.html#L21) also uses mixed-case `card-OrderNumber`.
- **Current Issue:** These hooks differ from the predominantly kebab-case class naming and are easy to miss in selector searches.
- **Proposed Change:** Use kebab-case for any renamed class, updating the template and every JS/CSS selector in the same change; first search `card-OrderNumber` for any hidden styling/consumer use.
- **Why It Helps:** Consistent selectors are easier to search and maintain.
- **Risk / Cross-File Dependencies:** **Medium.** `dragHandle` must be changed in the template and JS `handleClass` (and any CSS/legacy JS selector); preserve Sortable’s drag-handle behavior. Avoid renaming IDs, `data-*` fields, HTMX selectors, or form names as incidental cleanup.

## 3. Code Duplication (DRY)

### 3.1 Share order-detail data assembly while keeping both routes
- **Location:** [`app/main/routes.py`](../../../Documents/Proj/canteenClaude/app/main/routes.py#L26) and [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L76) both assemble order details for `order_confirmation/order_confirmation.html`; the former queries menu items inside a loop, while the latter performs a join.
- **Current Issue:** Two paths render the same template with overlapping context but separate query/aggregation logic.
- **Proposed Change:** Extract one focused order-detail data builder and use it in both route handlers; preserve not-found handling and any existing differences in context such as elapsed time.
- **Why It Helps:** Prevents fixes to order rendering or totals from diverging across URLs.
- **Risk / Cross-File Dependencies:** **High.** Keep `/confirmation/<order_number>` and `/order-confirmation/<order_number>` URLs and endpoint names (`main.confirmation`, `order_confirmation.index`) intact. Preserve template context keys (`order`, `order_items`, `order_number`, `items_with_details`, `total_amount`, `elapsed_time_mins` where supplied), tracking form field `order_number`, and API redirect URLs in `app/api/order.py`.

### 3.2 Extract the repeated menu-image transformation
- **Location:** [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L42) and [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L124) each contain nested upload, EXIF, RGB, thumbnail, and save logic.
- **Current Issue:** The image pipeline is duplicated inside two long handlers, making fixes to filename/format handling easy to apply inconsistently.
- **Proposed Change:** Extract one narrowly scoped image-save helper; leave request parsing, database updates, and route-specific responses in their handlers.
- **Why It Helps:** One source of truth for image processing reduces drift without introducing a general upload framework.
- **Risk / Cross-File Dependencies:** **High.** Preserve `UPLOAD_FOLDER`, `image_filename`, placeholder behavior, add/edit input names (`image`, `editImage` in the modal templates), redirect/JSON error behavior, and URLs serving `static/uploads/<filename>`.

### 3.3 Share order JSON serialization, not endpoint contracts
- **Location:** [`app/api/order.py`](../../../Documents/Proj/canteenClaude/app/api/order.py#L120) `get_orders()` and line 141 `get_active_orders()` construct the same list of order dictionaries.
- **Current Issue:** The response serialization is duplicated despite separate endpoint paths.
- **Proposed Change:** Extract a small serializer for the shared order shape and have both handlers use it. Do not silently add active-status filtering or change keys during this refactor.
- **Why It Helps:** API representations stay consistent when fields are maintained.
- **Risk / Cross-File Dependencies:** **Medium.** Preserve `/api/order/` and `/api/order/active`, JSON keys and ordering. Check consumers in [`app/static/js/pages/admin_order.js`](../../../Documents/Proj/canteenClaude/app/static/js/pages/admin_order.js) and legacy `static/js/admin_order.js` before removing either endpoint.

### 3.4 Avoid merging the two cart summary implementations without contract evidence
- **Location:** [`app/services/cart_service.py`](../../../Documents/Proj/canteenClaude/app/services/cart_service.py#L29) and [`app/api/cart.py`](../../../Documents/Proj/canteenClaude/app/api/cart.py#L57).
- **Current Issue:** Both calculate cart totals, but return different schemas (`cart_items`/`total` versus `items`/`total_price`) and are reached by different route families.
- **Proposed Change:** First map each route and client contract; only extract shared internal math if it can preserve both shapes and quantity/session semantics exactly.
- **Why It Helps:** Reduces actual repeated computation without coupling two incompatible response contracts.
- **Risk / Cross-File Dependencies:** **High.** Check `/cart/*`, `/api/cart/*`, `modals/cart.html`, `_cart_items.html`, `order.js`, `cart.js`, and any external API consumers. Do not rename `cartUpdated`, `#cart-modal-footer`, or cart form fields.

## 4. Long or Complex Functions

### 4.1 Split API analytics aggregation from HTTP response assembly
- **Location:** [`app/api/analytics.py`](../../../Documents/Proj/canteenClaude/app/api/analytics.py#L59) `get_analytics_data()` calculates time windows, queries orders, aggregates KPIs/charts, and builds the response through approximately line 257.
- **Current Issue:** One handler contains several distinct aggregation stages and broad exception handling, making individual calculations hard to test or review.
- **Proposed Change:** Extract focused pure helpers for per-period KPIs/chart groups and a response builder; keep the route responsible for parsing the range, invoking calculations, and returning the same status/payload.
- **Why It Helps:** Smaller units make analytics logic easier to reason about and validate independently.
- **Risk / Cross-File Dependencies:** **High.** Preserve accepted `range` values, timezone/window boundaries, endpoint `/api/analytics/`, all JSON key names/shapes, and the existing failure response. Verify any consumers before changing the route’s response.

### 4.2 Separate order creation stages
- **Location:** [`app/api/order.py`](../../../Documents/Proj/canteenClaude/app/api/order.py#L15) `create_order()` mixes request parsing, validation, order-number allocation, item lookup, persistence, cart cleanup, and response construction.
- **Current Issue:** A single handler owns request, business, persistence, and serialization responsibilities.
- **Proposed Change:** Extract small operations for validated customer/cart input, next order number, and response serialization; retain the route as orchestration and use early returns for invalid input.
- **Why It Helps:** Makes each failure path and business rule easier to inspect without introducing a broad service abstraction.
- **Risk / Cross-File Dependencies:** **High.** Preserve `customer_name`/`customer_phone` request fields, session keys `cart` and `verified_phone`, order status/timestamps, 400/404/201 behavior, response JSON keys, cart clearing timing, and redirect format consumed by `order.js`/`cart.js`.

### 4.3 Simplify menu grouping and remove duplicate category retrieval
- **Location:** [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L81) `manage_menu()` reads the ordered category list twice and scans all items once per category; its search filtering is commented out.
- **Current Issue:** Repeated database work and nested grouping obscure the single rendered structure; `search_query` is shown in the template even though filtering is disabled.
- **Proposed Change:** Reuse the ordered category collection and group items in one pass. Separately decide whether the search field is intended to filter; do not change current search behavior as part of this cleanup.
- **Why It Helps:** Removes redundant work and clarifies how categories map to item groups.
- **Risk / Cross-File Dependencies:** **Medium.** Preserve `items_by_category`, `categories`, and `search_query` context expected by `admin/manage_menu.html`, ordering, uncategorized behavior, and menu-item DOM IDs/data attributes used by `pages/admin_menu.js`.

## 5. Magic Values & Hygiene

### 5.1 Move static inline presentation into existing SCSS
- **Location:** Active inline styles appear in [`app/templates/main/index.html`](../../../Documents/Proj/canteenClaude/app/templates/main/index.html#L6), [`app/templates/menu/menu.html`](../../../Documents/Proj/canteenClaude/app/templates/menu/menu.html#L2), [`app/templates/admin_base.html`](../../../Documents/Proj/canteenClaude/app/templates/admin_base.html#L61), [`app/templates/admin/manage_menu.html`](../../../Documents/Proj/canteenClaude/app/templates/admin/manage_menu.html#L124), [`app/templates/admin/history.html`](../../../Documents/Proj/canteenClaude/app/templates/admin/history.html#L33), and modal/partial templates.
- **Current Issue:** Static widths, typography, colors, and spacing are mixed into markup; brand colors already have a token source in [`app/static/scss/abstracts/_variables.scss`](../../../Documents/Proj/canteenClaude/app/static/scss/abstracts/_variables.scss).
- **Proposed Change:** Move only fixed presentation to descriptive classes in the active SCSS entrypoint and reuse existing tokens where the visual values match. Keep data-driven widths (for example `item.width_percent` and order progress widths) inline.
- **Why It Helps:** Centralizes visual rules and keeps Jinja markup focused on content/behavior.
- **Risk / Cross-File Dependencies:** **Medium.** Update the same template nodes and SCSS selectors together; verify responsive behavior and pixel/layout parity. Preserve `id`, `class` hooks used by JS, HTMX `hx-target`/`hx-swap-oob`, and dynamic Jinja expressions.

### 5.2 Consolidate repeated backend order-status literals cautiously
- **Location:** Status constants already exist on [`app/models.py`](../../../Documents/Proj/canteenClaude/app/models.py#L57), but literals remain in [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L157), [`app/api/analytics.py`](../../../Documents/Proj/canteenClaude/app/api/analytics.py#L79), analytics services, [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L123), `templates/partials/_filter_dropdown.html`, `templates/partials/_order_status_card.html`, and JS status maps (`admin_order.js`, `admin_history.js`).
- **Current Issue:** Similar status names are repeated in Python, Jinja, and JS; `preparing` and other UI labels do not map one-to-one to the existing model constants.
- **Proposed Change:** First define/document the canonical status vocabulary and transitions. Use `Order.STATUS_*` for backend comparisons where equivalent; keep a small frontend mapping synchronized rather than attempting an artificial Python-to-JS shared-constant system.
- **Why It Helps:** Reduces spelling drift while making intentional UI/backend status differences visible.
- **Risk / Cross-File Dependencies:** **High.** Synchronize API status validation and timestamps, analytics/history filters, `_filter_dropdown.html`, `_order_status_card.html`, `admin_order.js`, and `admin_history.js`. Do not rename or collapse statuses (`pending`, `confirmed`, `ready`, `completed`, `cancelled`, `preparing`) without behavior approval.

### 5.3 Retain existing reusable template boundaries; consolidate only verified duplicate versions
- **Location:** Active reuse already exists for `partials/_history_content.html`, `partials/_pagination.html`, `partials/_order_status_card.html`, `partials/_toast_container.html`, and modal templates. Parallel legacy filter/page templates are present.
- **Current Issue:** Existing reusable fragments coexist with stale alternatives, which can invite unnecessary abstraction or editing the wrong copy.
- **Proposed Change:** Keep current partials; do not macro-ize trivial markup. Consolidate only duplicated blocks confirmed active in more than one live template, after the reference map in 1.3.
- **Why It Helps:** Avoids over-engineering while preserving the good reuse patterns already present.
- **Risk / Cross-File Dependencies:** **Medium.** For any moved fragment, update every `{% include %}`/`{% extends %}` and preserve template variables, input `name` attributes, HTMX IDs/targets/OOB selectors, and the active CSS/JS hooks.

## Prioritized batch execution order

1. **Completed — Safe hygiene:** Removed the approved debug traces, unused imports/assignments, duplicate return, unreachable block, and obsolete commented code. Seed/clear progress output and application contracts were preserved.
2. **Reference map and legacy verification:** Trace all Flask registrations, route/template render references, Jinja includes/extends, static imports, Sass imports, tests, and deployment use. Mark files as retained, active, or safe-to-remove; do not delete candidates before this pass.
3. **Focused behavior-preserving refactors:** Extract order-detail data building, menu-image processing, repeated order serialization, and small order/analytics calculations. Add targeted tests around existing response/context shapes and failure paths before changing callers.
4. **Style/hygiene alignment:** Move static inline presentation to SCSS, reuse existing tokens, and normalize selected class/function names with all dependent selectors/imports updated atomically. Keep dynamic styles and UI layout unchanged.
5. **Verified retirement and final validation:** Remove only approved orphaned files, then validate Flask route map, template rendering, Sass output, and relevant cart/order/admin UI flows; run existing tests and targeted checks.

## Batch 1 — Debug & dead code (approved and executed)

The exact approved change scope and rationale are recorded below. This batch is complete; it excludes later duplication, naming, SCSS, and file-retirement work.

### A. Remove transient debug output from active paths

Delete the following calls only:

- Python:
  - [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L176): `print("orders: ", orders)`.
  - [`app/main/routes.py`](../../../Documents/Proj/canteenClaude/app/main/routes.py#L56) and line 61: prints of the submitted digits and normalized order.
  - [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L42), lines 82, 87, and 121: raw query/order tracing.
  - [`app/cart/routes.py`](../../../Documents/Proj/canteenClaude/app/cart/routes.py#L35): `print("loading items")`.
  - [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L92), lines 134, 162, 167, and 251: generic image-failure text, uploaded file/name, `"here"`, and visibility tracing. Keep existing flash messages and JSON/error handling.
  - [`app/api/categories.py`](../../../Documents/Proj/canteenClaude/app/api/categories.py#L23) and line 49: add/delete request traces.
  - [`app/api/cart.py`](../../../Documents/Proj/canteenClaude/app/api/cart.py#L39): session cart contents.
  - [`app/api/authentication.py`](../../../Documents/Proj/canteenClaude/app/api/authentication.py#L40): logout message.
- JavaScript:
  - [`app/static/js/pages/admin_menu.js`](../../../Documents/Proj/canteenClaude/app/static/js/pages/admin_menu.js#L77), lines 110, 179, and 190: deletion, click-target, and form-data logs.
  - [`app/static/js/features/forms.js`](../../../Documents/Proj/canteenClaude/app/static/js/features/forms.js#L19): submitted `FormData`.
  - [`app/static/js/main.js`](../../../Documents/Proj/canteenClaude/app/static/js/main.js#L34): login redirect log.
  - [`app/static/js/admin.js`](../../../Documents/Proj/canteenClaude/app/static/js/admin.js#L7) and line 37: logout/toast initialization logs.
  - [`app/static/js/cart.js`](../../../Documents/Proj/canteenClaude/app/static/js/cart.js#L3), lines 12, 23, and 24: checkout progress/response logs.
  - [`app/static/js/order.js`](../../../Documents/Proj/canteenClaude/app/static/js/order.js#L7), lines 17 and 19: checkout/redirect logs.

**Reason:** These calls only trace already-handled work. Removing them does not require changes to routes, forms, template context, HTMX selectors, or response payloads.

**Keep unchanged:** `console.error()` and existing exception/error responses; intentional progress output in `seeddb.py` and `cleardb.py`; `test.py` pending confirmation whether it is a local utility. Do not edit logs in legacy scripts (`static/js/admin_menu.js`, `admin_menu2.js`, `admin_menu3.js`, `admin_analytics.js`, `order_menu.js`) in this batch; their use belongs in the later reference-map pass.

### B. Remove certain unreachable statements and unused imports

- [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L62): delete the second `if order:` and its `OrderItem` sum in `track()`. The preceding truthy-order path always redirects, so this block cannot execute. Keep `total_amount = 0` and the `total_amount` template argument to preserve the not-found context.
- [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L145): delete the second identical `return range(start_page, end_page + 1)`; the first return is the active result.
- Remove imports confirmed unused by each current module body:
  - [`app/__init__.py`](../../../Documents/Proj/canteenClaude/app/__init__.py#L11): remove `UserMixin`; keep `LoginManager`.
  - [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L8): remove the unused `get_dashboard_metrics` import; its only call is commented. Keep the active `get_dashboard_metrics2` import.
  - [`app/api/authentication.py`](../../../Documents/Proj/canteenClaude/app/api/authentication.py#L1): remove `abort`, `redirect`, and `url_for`; remove the unused `db` import; from Flask-Login remove `current_user`, `login_required`, `LoginManager`, and `UserMixin`; remove `wraps`. Keep `session`, `request`, `jsonify`, `login_user`, `logout_user`, `User`, and `admin_required`.
  - [`app/api/analytics.py`](../../../Documents/Proj/canteenClaude/app/api/analytics.py#L12): remove the unused `app` import.
  - [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L4): remove the unused `app` import.
  - [`app/api/categories.py`](../../../Documents/Proj/canteenClaude/app/api/categories.py#L1) and line 3: remove unused `redirect`, `url_for`, and `MenuItem`.
  - [`app/api/order.py`](../../../Documents/Proj/canteenClaude/app/api/order.py#L2): remove unused `url_for` and `sessions`.
  - [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L1): remove unused `timezone`.
  - [`app/services/order_service.py`](../../../Documents/Proj/canteenClaude/app/services/order_service.py#L93): remove the trailing unused imports of `db`, duplicate `Order`, `OrderItem`, and `cart_service`; keep the existing top-level `Order` import.
  - [`app/models.py`](../../../Documents/Proj/canteenClaude/app/models.py#L93): remove the later duplicate `datetime, timezone` import; the existing top-level import already supplies both.
- In [`app/api/analytics.py`](../../../Documents/Proj/canteenClaude/app/api/analytics.py#L95), remove unused assignments `has_prev_data`, `dishes_completed`, `meals_cooked`, `prev_meals`, `min_h`, and `max_h`. Their values do not contribute to the active response.

**Reason:** These are names or statements with no active use. Keep the application factory’s model-registration imports unchanged.

**Cross-file check:** The removed `get_dashboard_metrics` import is referenced only by commented analytics code. Preserve `admin.analytics_content`, its active service call, and all values passed to `partials/_analytics_content.html`.

### C. Remove commented-out alternative implementations in active files

Delete only these commented code blocks; retain explanatory comments and executable content:

- [`app/admin/routes.py`](../../../Documents/Proj/canteenClaude/app/admin/routes.py#L52): old analytics partial-render block and commented `metrics` assignment.
- [`app/order_confirmation/routes.py`](../../../Documents/Proj/canteenClaude/app/order_confirmation/routes.py#L127): fully commented duplicate `index()` route.
- [`app/api/menu.py`](../../../Documents/Proj/canteenClaude/app/api/menu.py#L44): old JSON-based add-item parsing/validation block; around line 218, the commented JSON `update_menu_item` implementation.
- [`app/api/analytics.py`](../../../Documents/Proj/canteenClaude/app/api/analytics.py#L180): commented recent-orders builder; around line 227, obsolete alternate payload definition. Keep the active response payload unchanged.
- [`app/templates/base.html`](../../../Documents/Proj/canteenClaude/app/templates/base.html#L89): fully commented old mobile navigation; keep the currently rendered navigation immediately above it.
- [`app/templates/admin/manage_menu.html`](../../../Documents/Proj/canteenClaude/app/templates/admin/manage_menu.html#L14): commented category-edit button; around line 152, old commented menu-item layout. Keep active markup and `toggleVisibility` behavior.
- [`app/templates/menu/menu.html`](../../../Documents/Proj/canteenClaude/app/templates/menu/menu.html#L160): commented legacy add-button markup and line 204's commented `order_menu.js` include. Keep active cart controls and `order.js`.

**Reason:** These alternatives are not executed/rendered and no longer describe the active paths.

**Risk / cross-file dependencies:** **Low** if only the exact comments are deleted. Do not change any executable endpoint, Jinja variable, input `name`, element ID, HTMX target/OOB selector, active script reference, or active CSS class.

### D. Explicitly defer uncertain candidates

Do not delete version-suffixed templates/services/scripts/styles, unregistered blueprint modules, the empty `app/api/orders.py`, or any CSS/SCSS file in Batch 1. Do not resolve the incomplete checkout call paths in `cart/routes.py` / `api/order.py` yet. These need the later route/deployment/API reference pass and may be behaviorally significant.

### Verification completed

1. Python AST parsing passed for all 13 touched Python modules.
2. Jinja parsing passed for the 3 changed templates.
3. The active-path `print()`/`console.log()` search found no remaining matches; remaining matches are in explicitly deferred legacy JS files.
4. JavaScript syntax checking could not run because Node.js is not installed in this environment. The JavaScript edits only delete `console.log()` statements; no executable expressions or imports were changed.
5. Route names, JSON payload keys, template context, form names, HTMX IDs/targets/OOB selectors, and rendered UI markup were not changed.

