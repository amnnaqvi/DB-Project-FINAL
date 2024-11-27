USE DBProject;

-- Table: User_Type
CREATE TABLE User_Type (
    type_id SMALLINT PRIMARY KEY IDENTITY (1, 1),
    role VARCHAR(10) NOT NULL CHECK (
        role IN ('Student', 'Faculty', 'Staff')
    )
);

-- Table: Admin
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY IDENTITY (1, 1),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    is_active BIT DEFAULT 1
);

-- Table: Notif_Type
CREATE TABLE Notif_Type (
    reference_id SMALLINT PRIMARY KEY IDENTITY (1, 1),
    type TEXT NOT NULL
);

-- Table: Category
CREATE TABLE Category (
    category_id TINYINT PRIMARY KEY IDENTITY (1, 1),
    category_type VARCHAR(50) NOT NULL CHECK (
        category_type IN (
            'Breakfast',
            'Lunch',
            'Custom Order',
            'Regular Item'
        )
    )
);

-- Table: SubCategory
CREATE TABLE SubCategory (
    sub_id TINYINT PRIMARY KEY IDENTITY(1,1),
    sub_type VARCHAR(50) NOT NULL CHECK (
        sub_type IN (
            'Seafood',
            'Continental',
            'Vegetarian',
            'Dessert',
            'Pasta',
            'Sandwich',
            'Salad',
            'Burger',
            'Roll',
            'Shake',
            'Soft Drink',
            'Juice',
            'Water'
        )
    ),
    category_id TINYINT FOREIGN KEY REFERENCES Category (category_id)
);

-- Table: Vendors
CREATE TABLE Vendors (
    vendor_id INT PRIMARY KEY IDENTITY(100,1),
    vendor_name VARCHAR(100) NOT NULL,
    image VARCHAR(100),
    password VARCHAR(100),
    is_active BIT DEFAULT 1,
    contact_number VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    admin_id INT FOREIGN KEY REFERENCES Admin (admin_id)
);

-- Table: Menu_Items
CREATE TABLE Menu_Items (
    item_id INT PRIMARY KEY IDENTITY(1,1),
    item_name VARCHAR(100) NOT NULL,
    vendor_id INT FOREIGN KEY REFERENCES Vendors (vendor_id),
    price DECIMAL(6, 2) NOT NULL,
    sub_id TINYINT FOREIGN KEY REFERENCES SubCategory (sub_id),
    units_in_stock SMALLINT NOT NULL,
    is_sold BIT DEFAULT 1, --If the item is sold by the vendor anymore or not
    description TEXT,
    image_url VARCHAR(100)
);

-- Table: Users
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1000,1),
    full_name VARCHAR(100) NOT NULL,
    type_id SMALLINT FOREIGN KEY REFERENCES User_Type (type_id),
    current_balance DECIMAL(10, 2) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    is_active BIT DEFAULT 1
);

-- Table: Orders
CREATE TABLE Orders (
    order_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES Users (user_id),
    vendor_id INT FOREIGN KEY REFERENCES Vendors (vendor_id),
    is_pickup BIT DEFAULT 1,
    total_cost DECIMAL(10, 2) NOT NULL,
    order_placed DATETIME NOT NULL,
    order_received DATETIME,
    status VARCHAR(9) NOT NULL CHECK (
        status IN (
            'Pending',
            'Confirmed',
            'Ready',
            'Making',
            'Completed'
        )
    )
);

-- Table: Order_Details
CREATE TABLE Order_Details (
    order_id INT FOREIGN KEY REFERENCES Orders (order_id),
    item_id INT FOREIGN KEY REFERENCES Menu_Items (item_id),
    quantity SMALLINT NOT NULL,
    price_per_unit DECIMAL(6, 2) NOT NULL,
    PRIMARY KEY (order_id, item_id)
);

-- Table: User_Balance_History
CREATE TABLE User_Balance_History (
    record_no INT PRIMARY KEY IDENTITY (1, 1),
    user_id INT FOREIGN KEY REFERENCES Users (user_id),
    amount DECIMAL(10, 2) NOT NULL,
    is_deposit BIT NOT NULL,
    record_date DATETIME NOT NULL,
    physical_payment BIT DEFAULT 1,
    order_id INT FOREIGN KEY REFERENCES Orders (order_id),
    admin_id INT FOREIGN KEY REFERENCES Admin (admin_id)
);

-- Table: User_Favorites
CREATE TABLE User_Favorites (
    user_id INT FOREIGN KEY REFERENCES Users (user_id),
    item_id INT FOREIGN KEY REFERENCES Menu_Items (item_id),
    added_at DATETIME NOT NULL,
    PRIMARY KEY (user_id, item_id)
);

-- Table: Notifications
CREATE TABLE Notifications (
    notif_no INT PRIMARY KEY IDENTITY (1, 1),
    user_id INT FOREIGN KEY REFERENCES Users (user_id),
    notif_type SMALLINT FOREIGN KEY REFERENCES Notif_Type (reference_id),
    notif_content VARCHAR(200),
    priority TINYINT NOT NULL CHECK (priority BETWEEN 1 AND 5),
    order_id INT FOREIGN KEY REFERENCES Orders (order_id),
    sent_at DATETIME NOT NULL
);

-- Table: Feedback
CREATE TABLE Feedback (
    user_id INT FOREIGN KEY REFERENCES Users (user_id),
    order_id INT FOREIGN KEY REFERENCES Orders (order_id),
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    rated_at DATETIME NOT NULL,
    PRIMARY KEY (user_id, order_id)
);

-- Table: Cart
CREATE TABLE Cart (
    user_id INT FOREIGN KEY REFERENCES Users (user_id),
    item_id INT FOREIGN KEY REFERENCES Menu_Items (item_id),
    quantity INT,
    PRIMARY KEY (user_id, item_id)
);

USE DBProject;

-- Insert User Types
INSERT INTO User_Type (role)
VALUES ('Student'),
       ('Faculty'),
       ('Staff');

USE DBProject;

-- Insert Admins
INSERT INTO Admin (name, email, password, is_active)
VALUES ('Admin1', 'admin1@habib.edu.pk', 'adminpass1', 1),
       ('Admin2', 'admin2@habib.edu.pk', 'adminpass2', 1);

USE DBProject;

-- Insert Categories
INSERT INTO Category (category_type)
VALUES ('Breakfast'),
       ('Lunch'),
       ('Custom Order'),
       ('Regular Item');

USE DBProject;

-- Insert SubCategories
INSERT INTO SubCategory (sub_type, category_id)
VALUES ('Sandwich', 1),
       ('Salad', 1),
       ('Soft Drink', 4),
       ('Seafood', 3),
       ('Continental', 2),
       ('Vegetarian', 2),
       ('Dessert', 4),
       ('Pasta', 2),
       ('Burger', 2),
       ('Roll', 2),
       ('Shake', 3),
       ('Juice', 4),
       ('Water', 4);

USE DBProject;

-- Insert Vendors
INSERT INTO Vendors (vendor_name, password, is_active, contact_number, email, admin_id)
VALUES ('Cafeela', 'cafee123', 1, '123-456-7890', 'cafeela@habib.edu.pk', 1),
       ('Hobnob', 'hb345', 1, '234-567-8901', 'hobnob@habib.edu.pk', 2),
       ('Cafe2Go', 'c2g892', 1, '345-678-9012', 'cafe2go@habib.edu.pk', 1),
       ('Grito', 'gt671', 1, '456-789-0123', 'grito@habib.edu.pk', 2),
       ('Dhabba', 'db567', 0, '111-222-3333', 'dhabba@habib.edu.pk', 1);

USE DBProject;

-- Insert Users
INSERT INTO Users (full_name, type_id, current_balance, email, password, is_active)
VALUES ('Amn Naqvi', 1, 630.00, 'sn11@st.habib.edu.pk', 'password123', 1),
       ('Rayyan Shah', 1, 480.00, 'rs12@st.habib.edu.pk', 'password234', 1),
       ('Umer Siddiqui', 1, 462.50, 'us13@st.habib.edu.pk', 'password345', 1),
       ('Qasim Pasta', 2, 670.00, 'qasim.pasta@sse.habib.edu.pk', 'password567', 1),
       ('Shafaq Mughal', 3, 641.51, 'shafaq.mughal@sse.habib.edu.pk', 'password321', 1),
       ('John Doe', 3, 400.00, 'john.doe@habib.edu.pk', 'forgotpassword', 0);

USE DBProject;

-- Insert Menu Items
INSERT INTO Menu_Items (item_name, vendor_id, price, sub_id, units_in_stock, description, image_url)
VALUES ('Chicken Sandwich', 100, 200.00, 1, 100, 'Grilled chicken sandwich', 'url1.jpg'),
       ('Grilled Salmon', 100, 300.00, 4, 50, 'Delicious grilled salmon seafood dish', 'url2.jpg'),
       ('Beef Burger', 100, 280.00, 9, 100, 'Juicy beef burger with toppings', 'url3.jpg');
       -- Additional menu items...

USE DBProject;

-- Insert Orders
INSERT INTO Orders (user_id, vendor_id, is_pickup, total_cost, order_placed, order_received, status)
VALUES (1000, 100, 1, 300.00, '2023-04-05 10:00:00', '2023-04-05 10:20:00', 'Ready'),
       (1001, 101, 0, 230.00, '2023-04-10 12:30:00', '2024-05-05 09:20:00', 'Making');

USE DBProject;
-- Insert Order Details
INSERT INTO Order_Details (order_id, item_id, quantity, price_per_unit)
VALUES (1, 3, 1, 300.00),
       (2, 2, 1, 150.00);

USE DBProject;

-- Insert User Balance History
INSERT INTO User_Balance_History (user_id, amount, is_deposit, record_date, physical_payment, order_id, admin_id)
VALUES (1000, 250.00, 0, '2023-05-01 10:30:00', 0, 2, 1),
       (1000, 500.00, 1, '2023-04-01 09:00:00', 0, NULL, 1);

USE DBProject;

-- Insert User Favorites
INSERT INTO User_Favorites (user_id, item_id, added_at)
VALUES (1000, 3, '2023-04-01 09:30:00'),
       (1002, 1, '2023-01-25 14:00:00');

USE DBProject;

-- Insert Notification Types
INSERT INTO Notif_Type (type)
VALUES ('Order Ready'),
       ('Order Delay'),
       ('Promotional Offer');

USE DBProject;

-- Insert Notifications
INSERT INTO Notifications (notif_type, notif_content, user_id, order_id, sent_at, priority)
VALUES (1, 'Order Ready! Please Collect it from Tapal', 1000, 1, '2023-04-05 10:15:00', 1),
       (2, 'Order Received', 1002, 2, '2023-04-10 12:00:00', 3);

USE DBProject;

-- Insert Feedback
INSERT INTO Feedback (user_id, order_id, rating, rated_at)
VALUES (1000, 1, 5, '2023-04-06 10:00:00'),
       (1001, 2, 4, '2023-04-11 14:00:00');

USE DBProject;

-- Insert Cart Items
INSERT INTO Cart (user_id, item_id, quantity)
VALUES (1003, 1, 2),
       (1003, 2, 4);
