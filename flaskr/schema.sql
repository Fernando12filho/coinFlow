DROP TABLE IF EXISTS investments;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

'amount: cryptocurrency amount bought'
'purchase_price: amount spent to buy certain amount of cryptocurrency'

CREATE TABLE investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    coin_name INTEGER NOT NULL,
    amount DECIMAL(16, 8) NOT NULL,
    purchase_date DATE NOT NULL,
    purchase_price DECIMAL(16, 2) NOT NULL,
    current_price DECIMAL(16, 2),
    profit_loss DECIMAL(16, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);