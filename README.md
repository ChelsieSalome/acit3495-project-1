# acit3495-project-1

* Salome Chelsie Lele Wambo
* Jaskirat Gill
* Jessica Shokouhi

## Overview

This project implements a containerized microservices data collection system.

The system consists of:

- Enter Data Web App (Flask)
- Authentication Service (Node.js)
- MySQL Database
- Analytics Service (Flask)
- Show Results Web App (Flask)
- MongoDB

The Enter Data Service collects customer, product, and sales data.
However, users must first be authenticated through the Authentication Service before they are allowed to submit data.
The Analytics Service processes the collected data and stores results in MongoDB.
The Show Results App displays the latest analytics to authenticated users.

All services communicate over Docker Compose's internal network.

---

## Architecture Flow

1. **User accesses Enter Data Web App**

   If not authenticated → user is redirected to `/login`.

2. **Login Process**

   The Enter Data app sends credentials to:
   ```
   auth-service:5001/login
   ```
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

4. **Analytics**

   The Analytics Service reads from MySQL, calculates results, and stores them in MongoDB.
   The Show Results App retrieves and displays the latest analytics from MongoDB.

---

## Technologies Used

**Enter Data Service**
- Python 3.11
- Flask
- mysql-connector-python

**Authentication Service**
- Node.js
- Express
- jsonwebtoken (JWT)

**Analytics Service**
- Python 3.11
- Flask
- mysql-connector-python
- pymongo

**Show Results Service**
- Python 3.11
- Flask
- pymongo

**Database**
- MySQL 8.0
- MongoDB

**Infrastructure**
- Docker
- Docker Compose
- OpenAPI 3.0

---

## Getting Started

### Prerequisites

Ensure the following are installed on your machine before proceeding:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

---

### Installation & Setup

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd acit3495-project-1
```

**2. Build and start all services**

```bash
docker compose up --build -d
```

**3. Verify all containers are running**

```bash
docker ps
```

---

### Accessing the Applications

| Service          | URL                           | Description                        |
|------------------|-------------------------------|------------------------------------|
| Enter Data App   | http://localhost:5000         | Add customers, products, and sales |
| Show Results App | http://localhost:5002/results | View latest analytics results      |

---

### Running Analytics

After entering data, trigger the analytics engine by running:

```bash
curl -X POST http://localhost:<analytics-port>/run-analytics
```

Then refresh the **Show Results App** to see updated analytics.

---

### Stopping the Application

```bash
docker compose down
```

To stop and remove all volumes (full reset):

```bash
docker compose down -v
```

---

### Troubleshooting

- **Containers not starting** — Check logs with `docker compose logs -f <service-name>`
- **Analytics not showing** — Ensure `/run-analytics` has been triggered at least once
- **Auth issues** — Confirm the `auth-service` container is healthy via `docker ps`

---

# Authentication Service

The Authentication Service is implemented as a separate microservice.

## Endpoints

POST `/login`

Request (JSON):
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```json
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
```json
{
  "valid": true,
  "username": "admin"
}
```

### Hardcoded Users

For simplicity:
```
admin / admin123
user  / user123
```

The goal of this service is to demonstrate microservice communication, not production-grade identity management.

---

# Database Service

### Jessica (mysql & Enter Data Web app)

## Directories:

## mysql/
- Dockerfile
- init.sql

## enter-data-app/
- app.py
- Dockerfile
- openapi.yml

---

Branch: `mysql-ed-app`

---

## Overview

The Enter Data Service is responsible for collecting data from users and storing it in the MySQL database.

This service allows users to:

- Add a new customer
- Add a new product
- Record a sale between a customer and a product

The service is built using **Python (Flask)** and connects to a **MySQL database container** using Docker.

---

## Technologies Used

- Python 3.11
- Flask
- mysql-connector-python
- MySQL 8.0
- Docker
- Docker Compose
- OpenAPI 3.0

---

## Database Design

The MySQL database (`project1`) contains three tables:

### 1. Customer

| Column        | Type                     | Description    |
|---------------|--------------------------|----------------|
| Customer_id   | INT (Auto Increment, PK) | Unique ID      |
| Customer_name | VARCHAR(100)             | Customer name  |
| Email         | VARCHAR(100)             | Customer email |

---

### 2. Products

| Column        | Type                     | Description   |
|---------------|--------------------------|---------------|
| Product_id    | INT (Auto Increment, PK) | Unique ID     |
| Product_name  | VARCHAR(100)             | Product name  |
| Product_price | DECIMAL(10,2)            | Product price |

---

### 3. Sale

| Column        | Type                         | Description                       |
|---------------|------------------------------|-----------------------------------|
| Sale_id       | INT (Auto Increment, PK)     | Unique sale record ID             |
| Purchase_date | DATE (Default: CURRENT_DATE) | Automatically stores today's date |
| Customer_id   | INT (FK)                     | References Customer(Customer_id)  |
| Product_id    | INT (FK)                     | References Products(Product_id)   |
| Quantity      | INT                          | Number of items purchased         |

The Sale table establishes a many-to-many relationship between Customers and Products.

---

## API Endpoints (OpenAPI 3.0)

The API is documented in `openapi.yml`.

### 1. Add Customer

**POST /**

Form Data:
- name (string)
- email (string)

Response:
- 200 OK – "Customer added"

---

### 2. Add Product

**POST /product**

Form Data:
- product_name (string)
- price (number)

Response:
- 200 OK – "Product added"

---

### 3. Record Sale

**POST /sale**

Form Data:
- customer_id (integer)
- product_id (integer)
- quantity (integer)

Response:
- 200 OK – "Sale recorded"

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

```bash
docker compose build
```

### Run the system

```bash
docker compose up
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

```bash
docker exec -it mysql mysql -u user -p
```

Use password: `password`

Example queries:

```sql
SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;
```

---

# Docker Compose: Line by Line Explanation

---

## Top-Level Configuration

```yaml
version: '3.8'
```
> Specifies the Docker Compose file format version. Version `3.8` supports advanced features like health check conditions in `depends_on`.

---

```yaml
services:
```
> Defines all the containers (services) that will be built and run as part of this application stack.

---

## MySQL Service

```yaml
  mysql:
```
> Declares a service named `mysql`. This is the internal reference name used by other services.

```yaml
    image: mysql:8.0
```
> Pulls the official **MySQL version 8.0** image from Docker Hub. No build step needed.

```yaml
    container_name: mysql-db
```
> Assigns a fixed name `mysql-db` to the running container, overriding the default auto-generated name.

```yaml
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
```
> Injects environment variables into the container at runtime. Values are read from the `.env` file using `${}` substitution — **credentials are never hardcoded**.

```yaml
    ports:
      - "3307:3306"
```
> Maps **host port 3307** to **container port 3306**. MySQL internally listens on `3306`, but is accessible from the host machine on `3307` to avoid conflicts with a locally installed MySQL instance.

```yaml
    volumes:
      - mysql_data:/var/lib/mysql
```
> Mounts a **named volume** `mysql_data` to MySQL's data directory. This ensures database data **persists** even if the container is stopped or removed.

```yaml
      - ./mysql-service/init.sql:/docker-entrypoint-initdb.d/init.sql
```
> Bind-mounts the local `init.sql` script into MySQL's init directory. MySQL **automatically executes** any `.sql` files in `/docker-entrypoint-initdb.d/` on first startup, used to create tables and seed data.

```yaml
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 20s
      retries: 10
```
> Defines a **health probe** that pings MySQL every `10s`. If no response within `20s`, it retries up to `10` times. Other services use this status before starting — preventing premature connections to an unready database.

---

## MongoDB Service

```yaml
  mongodb:
```
> Declares the MongoDB service, referenced internally by the name `mongodb`.

```yaml
    image: mongo:7.0
```
> Pulls the official **MongoDB version 7.0** image from Docker Hub.

```yaml
    container_name: mongodb
```
> Assigns the fixed container name `mongodb`.

```yaml
    ports:
      - "${MONGO_PORT}:27017"
```
> Maps the host port (from `.env`, e.g. `27017`) to container port `27017`. MongoDB's default listening port.

```yaml
    volumes:
      - mongo_data:/data/db
```
> Mounts named volume `mongo_data` to MongoDB's data directory `/data/db`, ensuring **data persistence** across container restarts.

```yaml
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 10s
      retries: 5
```
> Runs a `ping` command via the MongoDB shell (`mongosh`) every `10s`. Confirms MongoDB is **fully ready to accept connections** before dependent services start.

---

## Analytics Service

```yaml
  analytics-service:
```
> Declares the analytics Flask application service.

```yaml
    build: ./analytics-service
```
> Instead of pulling an image, Docker **builds a custom image** from the `Dockerfile` located in the `./analytics-service` directory.

```yaml
    container_name: analytics-service
```
> Assigns the fixed container name `analytics-service`.

```yaml
    ports:
      - "${ANALYTICS_SERVICE_PORT}:${ANALYTICS_SERVICE_PORT}"
```
> Dynamically maps the host port to the container port using the same value from `.env` (e.g. `5004:5004`).

```yaml
    environment:
      - MYSQL_HOST=${MYSQL_HOST}
      - MYSQL_PORT=${MYSQL_PORT}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MONGO_URI=${MONGO_URI}
      - MONGO_DB=${MONGO_DB}
      - ANALYTICS_COLLECTION=${ANALYTICS_COLLECTION}
      - ANALYTICS_SERVICE_PORT=${ANALYTICS_SERVICE_PORT}
      - FLASK_PORT=${ANALYTICS_SERVICE_PORT}
      - FLASK_DEBUG=${FLASK_DEBUG}
```
> Passes all required runtime configuration into the container. Keeps all secrets out of source code.

```yaml
    env_file:
      - .env
```
> Loads **all variables** from the `.env` file into the container's environment as a single block.

```yaml
    depends_on:
      mysql:
        condition: service_healthy
      mongodb:
        condition: service_healthy
```
> Enforces **startup order with health awareness**. The analytics service will not start until both `mysql` and `mongodb` report a **healthy** status.

```yaml
    volumes:
      - ./analytics-service:/app
```
> Bind-mounts the local `./analytics-service` directory into the container at `/app`. Enables **live code reloading** during development.

```yaml
    restart: on-failure
```
> Automatically **restarts the container** if it exits with a non-zero (error) code.

---

## Volumes

```yaml
volumes:
  mysql_data:
  mongo_data:
```
> Declares two **named volumes** managed by Docker. Data survives container removal and recreation.

---

## Networks

```yaml
networks:
  default:
    driver: bridge
```
> Explicitly defines the **default bridge network** for all services. Services communicate using their **service names as hostnames** (e.g. `mysql`, `mongodb`), while remaining isolated from the host network by default.

---

> **Key Docker Concepts Demonstrated:** Image pulling, custom builds, named volumes for persistence, bind mounts for init scripts and live reload, environment variable injection via `.env`, health checks for dependency management, port mapping, and bridge networking for inter-service communication.

---

## Design Decisions

- Flask was chosen because it is lightweight and easy to containerize.
- MySQL is used for structured relational data.
- MongoDB is used for storing unstructured analytics results.
- Docker Compose is used to allow communication between services using container names.
- The OpenAPI file documents the service endpoints clearly for integration with other microservices.
