CREATE TABLE IF NOT EXISTS user (
    id CHAR(14) PRIMARY KEY,
    avatar TEXT,
    username VARCHAR(255) NOT NULL,
    password TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,
    bio TEXT,
    UNIQUE (username(255)),
    UNIQUE (email(255))
);