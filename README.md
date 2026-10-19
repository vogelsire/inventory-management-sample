## Quick Start

### 1. Clone the repository

git clone https://github.com/vogelsire/inventory-management-sample.git
cd inventory-management-sample

### 2. Create and activate a virtual environment

python3 -m venv .venv

### 3. Install dependencies

pip3 install -r requirements.txt

### 4. Initialize the database

python3 manage.py migrate

python3 manage.py seed_demo_data

### 5. Start the application

python3 manage.py runserver

Open http://127.0.0.1:8000/

## Demo Accounts

| Role | Username | Password |
|---|---|---|
| Admin | demo_admin | DemoAdmin-123 |
| Shopper | shopper | ShopperDemo-123 |

Demo credentials are for local evaluation only.

## Table of Contents

- [Quick Start](#quick-start)
- [Demo Accounts](#demo-accounts)
- [Architecture & Technical Design](ARCHITECTURE.md)