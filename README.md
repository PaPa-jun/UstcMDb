# 数据库大作业——2024 年春季

## 项目介绍

基于 `flask` 开发的影评平台，参考豆瓣和 IMDb。

## 项目结构

```bash
.
├── README.md
├── apps    # 应用代码
│   ├── __init__.py
│   ├── config.py   # 配置文件
│   ├── main    # 住视图
│   │   ├── __init__.py
│   │   └── view.py
│   └── user    # 用户视图
│       ├── __init__.py
│       ├── module.py
│       └── view.py
├── assets  # 静态文件
│   ├── css
│   └── js
├── extensions  # 扩展
│   ├── __init__.py
│   └── mysql   # 数据库
│       ├── __init__.py
│       ├── module.py
│       └── schema.sql
├── requirements.txt
├── run.py  # 应用入口
└── templates   # 网页模板
    ├── base.html
    ├── main
    │   └── index.html
    └── user
        ├── login.html
        ├── profile.html
        └── register.html

12 directories, 19 files
```

## 项目运行

### 安装依赖

```bash
pip install requirements.txt
```

### 运行

```bash
python run.py -m develop
```

```bash
usage: run.py [-h] [-m MODE]

Run the web application.

options:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  Mode in which to run the app, MODE: default, develop, test
```

## 更新日志

- 2024-6-6：完成基础用户登陆验证模块
