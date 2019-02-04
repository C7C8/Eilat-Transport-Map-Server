#!/usr/bin/env python3
from flask import Flask, Blueprint
from flask_restplus import Api, Resource, reqparse

import db


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


@ns.route("/flights")
class HelloWorld(Resource):
    def get(self):
        flights = db.get_flights()
        return response(True, "Found {} flights".format(len(flights)), "flights", flights)


# Run Flask development server.
# DO NOT USE IN PRODUCTION, DO IT PROPERLY WITH WSGI
if __name__ == "__main__":
    app.run()
