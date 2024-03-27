#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def restaurants():
    restaurants = Restaurant.query.all()
    respond_body = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants]
    return make_response(respond_body, 200)

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        if request.method == "GET":
            respond_body = restaurant.to_dict()
            status_code = 200
        elif request.method == "DELETE":
            db.session.delete(restaurant)
            db.session.commit()
            respond_body = {}
            status_code = 204

    else:
        respond_body = {"error": "Restaurant not found"}
        status_code = 404
    return make_response(respond_body, status_code)

@app.route('/pizzas')
def pizzas():
    pizzas = Pizza.query.all()
    response_body = [pizza.to_dict(rules=('-restaurant_pizzas', )) for pizza in pizzas]
    return make_response(response_body, 200)


@app.route('/restaurant_pizzas', methods=["POST"])
def create_restaurantpizza():
    form_data = request.get_json()
    price = form_data.get('price')
    pizza_id = form_data.get('pizza_id')
    restaurant_id = form_data.get('restaurant_id')

    try:
        new_restaurant_pizza = RestaurantPizza(price=price, 
                                            pizza_id=pizza_id, 
                                            restaurant_id=restaurant_id)
        
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return make_response(new_restaurant_pizza.to_dict(), 201)
    except ValueError:
        respond_body = {"errors": ["validation errors"]}
        return make_response(respond_body, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
