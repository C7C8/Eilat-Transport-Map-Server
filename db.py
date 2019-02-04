import pymysql

from conf import conf

def get_db():
    """Get a DB cursor, because persistent DB connections = bad"""
    connection = pymysql.connect(**(conf()["db"]))
    return connection.cursor()
