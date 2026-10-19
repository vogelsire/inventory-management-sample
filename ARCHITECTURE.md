
# Inventory Management Sample — Architecture

## 1. Overview

A inventory management application built with Django and Django REST Framework.

Features:
- Public product storefront.
- Staff-only product management.
- Authenticated purchasing and personal order history.
- REST API for products, purchases and orders.
- Seeded demo data for local evaluation.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Backend | Python, Django | Application logic, ORM and authentication |
| REST API | Django REST Framework | API endpoints and serialization |
| Database | SQLite | Local data persistence |
| Frontend | Django Templates, HTML, CSS | Web interface |
| Filtering | django-filter | API filtering support |
| CORS | django-cors-headers | Cross-origin configuration support |

## 3. System Architecture

The application separates responsibilities into:

- **Models:** Database entities and relationships.
- **Serializers:** API validation and data transformation.
- **Views:** Web and API request handling.
- **Permissions:** Access control for staff and authenticated users.
- **Templates:** Browser-based interface.
- **Management commands:** Reproducible demo data setup.

The web interface and REST API share the same models and database.

Main flows:
- **Browse:** Retrieve active products and display them as HTML or JSON.
- **Manage:** Staff users create, update and delete products.
- **Purchase:** Validate the request, deduct stock and create an order transactionally.

## 4. Database Schema

### 4.1 Product

| Field | Type | Description |
|---|---|---|
| id | Primary key | Product identifier |
| name | String | Product name |
| sku | String, unique | Unique stock keeping unit |
| description | Text | Product description |
| price | Decimal | Current selling price |
| stock | Positive integer | Available quantity |
| is_active | Boolean | Sales availability |
| created_at | DateTime | Creation time |
| updated_at | DateTime | Last update time |

### 4.2 Order

| Field | Type | Description |
|---|---|---|
| id | Primary key | Order identifier |
| user_id | Foreign key | Purchasing user |
| created_at | DateTime | Order creation time |

### 4.3 OrderItem

| Field | Type | Description |
|---|---|---|
| id | Primary key | Order-item identifier |
| order_id | Foreign key | Parent order |
| product_id | Foreign key | Purchased product |
| quantity | Positive integer | Quantity purchased |
| unit_price | Decimal | Price at purchase time |

Relationships:
- One user can have many orders.
- One order can contain many order items.
- One product can appear in many order items.

`OrderItem.unit_price` preserves historical pricing. Subtotal is calculated as `quantity × unit_price`.

Product SKUs are unique. Order items protect referenced products from deletion, while deleting an order cascades to its items.

## 5. Concurrency Strategy

The buy endpoint protects inventory integrity through conditional database updates and atomic transactions.

### 5.1 Conditional Stock Deduction

The endpoint deducts stock using a conditional database update:

```python
Product.objects.filter(
    id=product_id,
    is_active=True,
    stock__gte=quantity,
).update(
    stock=models.F("stock") - quantity
)
```

The stock sufficiency check and deduction happen in a single database operation. `F("stock")` performs the calculation in the database, avoiding stale stock values from application memory.

The application checks the affected-row count:
- **1 row updated:** Stock was deducted successfully.
- **0 rows updated:** The product is unavailable, inactive or has insufficient stock; the purchase is rejected.

For example, if only one unit remains and two users attempt to buy it concurrently, only one request can successfully deduct that unit. The other request cannot deduct stock below zero.

### 5.2 Transactional Order Creation

Stock deduction and order creation run inside `transaction.atomic()`:

1. Conditionally deduct stock.
2. Reject the purchase if no row was updated.
3. Create the order and order item using the database product price.
4. Commit the transaction.

If order creation fails with an exception, the transaction rolls back the stock deduction. This prevents stock from being permanently deducted without a corresponding order.

### 5.3 Additional Safeguards

- The endpoint requires authentication.
- Quantity must be a positive integer.
- Inactive or unavailable products cannot be purchased.
- The server determines the price; client-supplied prices are not trusted.
- Conditional updates prevent overselling, while transactions protect consistency.

SQLite is suitable for local evaluation but has limited write concurrency. For production workloads with higher concurrent purchasing traffic, MySQL with the InnoDB storage engine would be a suitable choice because it supports transactions and row-level locking.

## 6. Authentication and Authorization

| Operation | Access |
|---|---|
| Browse products | Public |
| Purchase products | Authenticated users |
| View order history | Authenticated users; own orders only |
| Manage products | Staff users |
| Django administration | Authorized staff or superusers |

Product API writes require staff permissions. Browser inventory pages are staff-restricted, and order queries are filtered by the current user.

Django authentication and CSRF protection are used for browser-based forms.

## 7. API Design

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/products/` | GET | List products |
| `/api/products/` | POST | Create product; staff only |
| `/api/products/{id}/` | GET | Retrieve product |
| `/api/products/{id}/` | PUT / PATCH | Update product; staff only |
| `/api/products/{id}/` | DELETE | Delete product; staff only |
| `/api/buy/` | POST | Purchase product; authenticated |
| `/api/my-orders/` | GET | List the current user's orders |

The purchase endpoint accepts a product ID and quantity. The server retrieves the price from the database rather than trusting client-supplied prices.

## 8. Technical Trade-offs

### Django and Django REST Framework

- **Benefits:** Built-in authentication, ORM, migrations and API support.
- **Trade-off:** Framework conventions add some overhead but support rapid development.

### SQLite

- **Benefits:** Simple setup without a separate database server; suitable for local evaluation.
- **Trade-off:** Limited write concurrency under heavier workloads. MySQL with InnoDB is a suitable production alternative.

### Django Templates

- **Benefits:** One deployable application without a separate frontend build.
- **Trade-off:** Less flexible for highly interactive interfaces than a separate frontend.

### Conditional Updates and Transactions

- **Benefits:** Reduce overselling risk and keep stock changes consistent with order creation.
- **Trade-off:** Database locking behavior varies; concurrent workloads still require testing.

### Seeded Demo Data

- **Benefits:** Reproducible setup without committing a local database.
- **Trade-off:** Evaluators must run migrations and the seed command. Demo credentials are for local evaluation only.

## 9. Local Setup

Prerequisites: Python and pip.

```bash
git clone https://github.com/vogelsire/inventory-management-sample.git
cd inventory-management-sample

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed_demo_data
python3 manage.py runserver
```

Open `http://127.0.0.1:8000/`.

See `README.md` for demo credentials and additional setup instructions.

## 10. Potential Future Improvements

- Migrate to MySQL with InnoDB for production workloads.
- Add automated tests for concurrent purchases and transaction rollback.
- Improve API pagination, filtering and error responses.
- Add logging, monitoring and rate limiting.
- Configure production secrets through environment variables.
