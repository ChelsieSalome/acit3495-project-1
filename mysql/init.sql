-- mysql/init.sql

CREATE TABLE Customer (
    Customer_id INT AUTO_INCREMENT PRIMARY KEY,
    Customer_name VARCHAR(100),
    Email VARCHAR(100)
);

CREATE TABLE Products (
    Product_id INT AUTO_INCREMENT PRIMARY KEY,
    Product_name VARCHAR(100),
    Product_price DECIMAL(10,2)
);

CREATE TABLE Sale (
    Sale_id INT AUTO_INCREMENT PRIMARY KEY,
    Purchase_date DATE,
    Customer_id INT,
    Product_id INT,
    Quantity INT,
    FOREIGN KEY (Customer_id) REFERENCES Customer(Customer_id),
    FOREIGN KEY (Product_id) REFERENCES Products(Product_id)
);
