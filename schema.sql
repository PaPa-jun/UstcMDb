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

CREATE TABLE IF NOT EXISTS movie (
    id CHAR(14) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT NOT NULL,
    rating INT,
    plot TEXT
);

CREATE TABLE IF NOT EXISTS director (
    id CHAR(14) PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS cast (
    id CHAR(14) PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS genre (
    id CHAR(14) PRIMARY KEY,
    genre VARCHAR(255)
);