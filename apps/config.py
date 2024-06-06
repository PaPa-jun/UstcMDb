class Base:
    SECRET_KEY = "you-shall-no-pass"
    ENV = "base"
    SQL = {
        "host" : "localhost",
        "port" : 3306,
        "user" : "root", 
        "password" : "Pyf20030317",
        "schema" : "ustcMDb",
        "charset" : 'utf8mb4'
    }
    DEBUG = False
    TESTING = False

class Develop(Base):
    ENV = "development"
    DEBUG = True

class Test(Base):
    ENV = "test"
    TESTING = True

config_map = {
    "default" : Base,
    "develop" : Develop,
    "test" : Test
}