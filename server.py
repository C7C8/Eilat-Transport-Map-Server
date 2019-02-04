#!/usr/bin/env python3
from flask import Flask, Blueprint
from flask_restplus import Api, Resource, reqparse
import pymysql
import json
import sys


def perror(*args, **kwargs):
    """Lazy way of writing to stderr"""
    print(*args, file=sys.stderr, **kwargs)


# Load server configuration file
conf = {
    "db": {
        "host": "localhost",
        "port": 3306,
        "user": "eilat_transport",
        "password": "password",
        "schema": "eilat_transport"
    }
}
try:
    with open("conf.json", "r") as file:
        conf = json.load(file)
except FileNotFoundError:
    perror("Failed to load conf.json!")


# Flask setup
app = Flask(__name__)
apiV1 = Blueprint("api", __name__)
api = Api(apiV1, title="Eilat map data service", description="Eilat map data service")
ns = api.namespace("api", description="Eilat map data service endpoints")
app.register_blueprint(apiV1)


def response(success, message, descriptor=None, payload=None):
    """Helper to generate a JSON response in a standard format"""
    if descriptor is None:
        return {"status": "success" if success else "error", "message": message}
    else:
        return {"status": "success" if success else "error", "message": message, descriptor: payload}


def get_db():
    """Get a DB cursor, because persistent DB connections = bad"""
    connection = pymysql.connect(**(conf["db"]))
    return connection.cursor()


@ns.route("/hello")
class HelloWorld(Resource):
    def get(self):
        return response(True, "Hello world!")


# Run Flask development server.
# DO NOT USE IN PRODUCTION, DO IT PROPERLY WITH WSGI
if __name__ == "__main__":
    app.run()
