-- 用户表
CREATE TABLE IF NOT EXISTS user (
    id CHAR(14) PRIMARY KEY,
    avatar VARCHAR(255),
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    bio TEXT,
    birthday DATE
);

-- 管理员表
CREATE TABLE IF NOT EXISTS admin(
    id CHAR(14) PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES user(id)
);

-- 电影表
CREATE TABLE IF NOT EXISTS movie (
    id CHAR(14) PRIMARY KEY,
    poster VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    year INT,
    duration INT,
    rating DECIMAL(2, 1),
    plot TEXT,
    trailer VARCHAR(255),
    genres TEXT
);

-- 工作人员表
CREATE TABLE IF NOT EXISTS worker (
    id CHAR(14) PRIMARY KEY,
    avatar VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    gender CHAR(1),
    birth DATE,
    job VARCHAR(255),
    bio TEXT
);

-- 电影和工作人员关系表
CREATE TABLE IF NOT EXISTS movie_worker (
    movie_id CHAR(14),  -- 外键指向movie
    worker_id CHAR(14),  -- 外键指向worker
    job VARCHAR(255),
    PRIMARY KEY (movie_id, worker_id),
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    FOREIGN KEY (worker_id) REFERENCES worker(id)
);

-- 影评表
CREATE TABLE IF NOT EXISTS review (
    id CHAR(14) PRIMARY KEY,  -- 使用UUID
    movie_id CHAR(14),  -- 外键指向movie
    user_id CHAR(14),  -- 外键指向user
    content TEXT NOT NULL,
    writer_id CHAR(14),
    likes INT DEFAULT 0,
    date DATE,
    rating DECIMAL(2, 1),
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (writer_id) REFERENCES user(id)
);

-- 电影图表
CREATE TABLE IF NOT EXISTS movie_figure (
    id CHAR(14) PRIMARY KEY,  -- 使用UUID
    movie_id CHAR(14),  -- 外键指向movie
    FOREIGN KEY (movie_id) REFERENCES movie(id)
);

-- 工作人员图表
CREATE TABLE IF NOT EXISTS worker_figure (
    id CHAR(14) PRIMARY KEY,  -- 使用UUID
    worker_id CHAR(14),  -- 外键指向worker
    FOREIGN KEY (worker_id) REFERENCES worker(id)
);
