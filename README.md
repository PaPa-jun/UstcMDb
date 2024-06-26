# 数据库大作业——2024 年春季

## 项目介绍

基于 `flask` 开发的影评平台，参考豆瓣和 IMDb。

## 项目结构

```bash
.
├── README.md
├── apps
│   ├── __init__.py
│   ├── cast
│   │   ├── __init__.py
│   │   └── view.py
│   ├── config.py
│   ├── main
│   │   ├── __init__.py
│   │   └── view.py
│   ├── menu
│   │   ├── __init__.py
│   │   └── view.py
│   ├── movie
│   │   ├── __init__.py
│   │   └── view.py
│   ├── search
│   │   ├── __init__.py
│   │   ├── module.py
│   │   └── view.py
│   └── user
│       ├── __init__.py
│       ├── module.py
│       └── view.py
├── assets
│   ├── css
│   │   ├── base.css
│   │   ├── cast_detail.css
│   │   ├── classification.css
│   │   ├── comment.css
│   │   ├── login.css
│   │   ├── main_index.css
│   │   ├── menu.css
│   │   ├── movie_detail.css
│   │   ├── profile.css
│   │   ├── profile_modify.css
│   │   ├── recent_25.css
│   │   ├── register.css
│   │   ├── search_results.css
│   │   └── top_25.css
│   ├── images
│   │   └── avatars
│   │       └── fixed_pics
│   │           └── default.jpg
│   └── js
│       ├── base.js
│       ├── comments.js
│       └── onclick.js
├── data
│   ├── casts
│   │   └── casts.json
│   ├── movies
│   │   ├── imdb_popular_25_movies.json
│   │   └── imdb_top_25_movies.json
│   ├── reviews
│   │   └── reviews.json
│   ├── src
│   │   ├── __pycache__
│   │   │   └── module.cpython-312.pyc
│   │   ├── main.py
│   │   └── module.py
│   └── users
│       └── users.json
├── extensions
│   ├── __init__.py
│   ├── interface
│   │   ├── __init__.py
│   │   └── module.py
│   └── mysql
│       ├── __init__.py
│       └── module.py
├── requirements.txt
├── run.py
├── schema.sql
└── templates
    ├── back_up_base.html
    ├── base.html
    ├── casts
    │   └── detail.html
    ├── main
    │   ├── back_up_index.html
    │   └── index.html
    ├── menu
    │   └── index.html
    ├── movie
    │   ├── classification.html
    │   ├── detail.html
    │   ├── recent.html
    │   └── top.html
    ├── new_base.html
    ├── search
    │   └── results.html
    ├── test.css
    ├── test.html
    ├── test.js
    └── user
        ├── login.html
        ├── profile.html
        ├── profile_modify.html
        └── register.html

31 directories, 70 files
```

## 项目运行

### 安装依赖

```bash
pip install requirements.txt
```

### 基础设置

首先按照自己的数据库信息更改 `apps/config.py`：

```py
class Base:
    SECRET_KEY = "you-shall-no-pass"
    ENV = "base"
    SQL = {
        "host" : "your host",
        "port" : 3306,
        "user" : "root", 
        "password" : "your password",
        "schema" : "your schema",
        "charset" : 'utf8mb4'
    }
    DEBUG = False
    TESTING = False
```

同样，更新 `data/src/main.py`：

```py
database_host = "your host"
database_password = "your password"
database_schema = "your schema"
```

更新 Google YouTube API Key：

```py
GOOGLE_YOUTUBE_API_KEY = "Your API Key"
```

### 网站运行

```bash
python run.py
```

#### 可选参数：

```bash
usage: run.py [-h] [-m MODE]

Run the web application.

options:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  Mode in which to run the app, MODE: default, develop, test
```

### 爬取数据

```
python ./data/src/main.py
```

## 更新日志

- 2024-6-6：完成基础用户登陆验证模块，创建 IMDb 对象爬取 Top 25 的电影；
- 2024-6-15：优化数据库表结构，完成用户信息展示与修改，定义基础用户交互接口； 
- 2024-6-16: 爬虫更新；实现搜索功能；实现比较完整的交叉信息展示；
- 2024-6-19：修复一些 bug，完成点赞功能。

## 暂停更新说明

由于作者在期末考试，本仓库目前暂时停止更新，可能会在考完后完善项目功能，重构项目代码。
