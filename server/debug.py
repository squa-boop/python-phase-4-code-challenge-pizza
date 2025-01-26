#!/usr/bin/env python3

from app import app
from models import db, Restaurant, Pizza, RestaurantPizza

if __name__ == '__main__':
    with app.app_context():
        import ipdb  # Ensure ipdb is installed
        ipdb.set_trace()  # This will pause execution here and start the debugger
