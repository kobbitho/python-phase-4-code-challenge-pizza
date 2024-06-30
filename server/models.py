from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan", overlaps="restaurant,restaurant_pizzas")

    # add serialization rules
    serialize_rules = ('-pizzas',)
    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [restaurant_pizza.to_dict() for restaurant_pizza in self.pizzas]
        }
        return data
    
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurants = db.relationship('RestaurantPizza', back_populates='pizza', cascade="all, delete-orphan", overlaps="pizza,restaurant_pizzas")

    # add serialization rules
    serialize_rules = ('-restaurants',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"
    
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }
        return data


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)

    # add relationships
    restaurant = db.relationship('Restaurant', backref='restaurant_pizzas', overlaps="pizzas,restaurant")
    pizza = db.relationship('Pizza', backref='restaurant_pizzas', overlaps="restaurants,pizza")


    # add serialization rules
    # add validation
    @validates("price")
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price
    
    def to_dict(self):
        data = {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'restaurant': {
                'id': self.restaurant.id,
                'name': self.restaurant.name,
                'address': self.restaurant.address
            },
            'pizza': {
                'id': self.pizza.id,
                'name': self.pizza.name,
                'ingredients': self.pizza.ingredients
            }
        }
        return data
    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
