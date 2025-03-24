DROP TABLE IF EXISTS subscribers;
DROP TABLE IF EXISTS investments;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    /*TODO is_subscribed*/
    is_subscribed BOOLEAN DEFAULT FALSE
);

CREATE TABLE investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    coin_name TEXT NOT NULL,
    amount DECIMAL(16, 8) NOT NULL,
    purchase_date DATE NOT NULL,
    purchase_price DECIMAL(16, 2) NOT NULL,
    current_price DECIMAL(16, 2),
    profit_loss DECIMAL(16, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  -- Optional for guests (null allowed)
    email TEXT UNIQUE NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);




