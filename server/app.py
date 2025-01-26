#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Correct base directory
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")  # Database URI

app = Flask(__name__)  # Create Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE  # Database URI config
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable modification tracking
app.json.compact = False  # Make JSON output readable

migrate = Migrate(app, db)  # Initialize Flask-Migrate
db.init_app(app)  # Initialize database connection

# Route to get all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    # Use to_dict with include_restaurant_pizzas=False to exclude 'restaurant_pizzas'
    return jsonify([restaurant.to_dict(include_restaurant_pizzas=False) for restaurant in restaurants]), 200

# Route to get a specific restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    # Use the to_dict method to serialize the restaurant and include restaurant_pizzas
    return jsonify(restaurant.to_dict()), 200

# Route to delete a restaurant by ID
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

# Route to get all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200

# Route to create a new restaurant pizza (many-to-many relationship)
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        # Validate price is within the specified range
        if not (1 <= data['price'] <= 30):
            raise ValueError("validation errors")  # Match test expectation for validation

        # Create the new restaurant_pizza entry
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Return the created entry with all relevant data
        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant_id": restaurant_pizza.restaurant_id,
            "pizza": restaurant_pizza.pizza.to_dict(),
            "restaurant": restaurant_pizza.restaurant.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400  # Return validation error if price is invalid

# Index route for a simple landing page
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Main entry point to start the Flask app
if __name__ == "__main__":
    app.run(port=5555, debug=True)
