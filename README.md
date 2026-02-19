# acit3495-project-1

### Overview

This project implements a containerized microservices data collection system.

The system consists of:

- Enter Data Web App (Flask)

- Authentication Service (Node.js)

- MySQL Database

The Enter Data Service collects customer, product, and sales data.
However, users must first be authenticated through the Authentication Service before they are allowed to submit data.

All services communicate over Docker Compose’s internal network.

## Architecture Flow

1. **User accesses Enter Data Web App**

If not authenticated → user is redirected to /login.

2. **Login Process**

The Enter Data app sends credentials to:

auth-service:5001/login


If valid, the Authentication Service returns a JWT token.

The token is stored in an HTTP-only cookie.

3. **Accessing Protected Endpoints**

Before allowing access to:
```
/

/product

/sale
```

The Enter Data app verifies the token by calling:
```
auth-service:5001/verify
```

If the token is valid → request proceeds.
If invalid → user is redirected to login.

## Technologies Used

**Enter Data Service**

- Python 3.11
- Flask
- mysql-connector-python

**Authentication Service**

- Node.js
- Express
- jsonwebtoken (JWT)

**Database**

- MySQL 8.0
- MongoDB

**Infrastructure**

- Docker
- Docker Compose
- OpenAPI 3.0


# Authentication Service

The Authentication Service is implemented as a separate microservice.

## Endpoints

POST `/login`

Request (JSON):
```
{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```
{
  "token": "<jwt_token>",
  "expires_in": 3600
}
```

GET `/verify`

Header:
```
Authorization: Bearer <token>
```

Response:
```
{
  "valid": true,
  "username": "admin"
}
```

### Hardcoded Users

For simplicity:
```
admin / admin123

user / user123
```

The goal of this service is to demonstrate microservice communication, not production-grade identity management.


# Database Service

### Jessica (mysql & Enter Data Web app)

## Directories:

## mysql/
-Dockerfile
-init.sql

## enter-data-app/
-app.py
-Dockerfile
-openapi.yml

---

Branch: `mysql-ed-app`

---

## Overview

The Enter Data Service is responsible for collecting data from users and storing it in the MySQL database.

This service allows users to:

* Add a new customer
* Add a new product
* Record a sale between a customer and a product

The service is built using **Python (Flask)** and connects to a **MySQL database container** using Docker.

---

## Technologies Used

* Python 3.11
* Flask
* mysql-connector-python
* MySQL 8.0
* Docker
* Docker Compose
* OpenAPI 3.0

---

## Database Design

The MySQL database (`project1`) contains three tables:

### 1. Customer

| Column | Type | Description |
| ------------- | ------------------------ | -------------- |
| Customer_id | INT (Auto Increment, PK) | Unique ID |
| Customer_name | VARCHAR(100) | Customer name |
| Email | VARCHAR(100) | Customer email |

---

### 2. Products

| Column | Type | Description |
| ------------- | ------------------------ | ------------- |
| Product_id | INT (Auto Increment, PK) | Unique ID |
| Product_name | VARCHAR(100) | Product name |
| Product_price | DECIMAL(10,2) | Product price |

---

### 3. Sale

| Column | Type | Description |
|----------------|--------------------------|--------------------------------------|
| Sale_id | INT (Auto Increment, PK) | Unique sale record ID |
| Purchase_date | DATE (Default: CURRENT_DATE) | Automatically stores today's date |
| Customer_id | INT (FK) | References Customer(Customer_id) |
| Product_id | INT (FK) | References Products(Product_id) |
| Quantity | INT | Number of items purchased |


The Sale table establishes a many-to-many relationship between Customers and Products.

---

## API Endpoints (OpenAPI 3.0)

The API is documented in `openapi.yml`.

### 1. Add Customer

**POST /**

Form Data:

* name (string)
* email (string)

Response:

* 200 OK – "Customer added"

---

### 2️. Add Product

**POST /product**

Form Data:

* product_name (string)
* price (number)

Response:

* 200 OK – "Product added"

---

### 3️. Record Sale

**POST /sale**

Form Data:

* customer_id (integer)
* product_id (integer)
* quantity (integer)

Response:

* 200 OK – "Sale recorded"

---

## How It Works

1. The user submits form data through the Flask web interface.
2. The Flask app receives the POST request.
3. The app connects to the MySQL container using:

```
host: mysql
user: user
password: password
database: project1
```

4. SQL INSERT queries are executed.
5. Data is committed and stored inside the MySQL database container.

The MySQL container name is used as the hostname because Docker Compose automatically creates an internal network for service communication.

---

## Docker Setup

### Build the containers

From the project root directory:

```
docker-compose build
```

### Run the system

```
docker-compose up
```

The Enter Data Service will run at:

```
http://localhost:5000
http://localhost:5000/sale
http://localhost:5000/product

```

---

## Testing the Database

To access the MySQL container:

```
docker exec -it mysql mysql -u user -p
```

Use password: password

Example query:

```
SELECT * FROM Customer;
SELECT * FROM Products;
SELECT * FROM Sale;
```

---

## Design Decisions

* Flask was chosen because it is lightweight and easy to containerize.
* MySQL is used for structured relational data.
* Docker Compose is used to allow communication between services using container names.
* The OpenAPI file documents the service endpoints clearly for integration with other microservices.

---




