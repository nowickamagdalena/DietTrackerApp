from flask_login import UserMixin
from sqlalchemy import ForeignKey
from .__init__ import db

#table for users
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    dailyCalGoal = db.Column(db.Integer)
    proteinPercentGoal = db.Column(db.Integer)
    fatPercentGoal = db.Column(db.Integer)
    carbsPercentGoal = db.Column(db.Integer)
    
    def __repr__(self):
        return "<User(id='%d' name='%s', email='%s', password='%s', cal_goal='%s', prot_goal='%s', fat_goal='%s', carb_goal='%s')>"%\
            (self.id, self.name, self.email, self.password, self.dailyCalGoal, self.proteinPercentGoal, self.fatPercentGoal, self.carbsPercentGoal)

#table for meals
class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "<Meal(id='%d' type='%s', date='%s', user='%s')>"%(self.id, self.type, self.date, self.user)

#table for ingredients of meals
class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    meal = db.Column(db.Integer, ForeignKey('meals.id'), primary_key=True) 
    food_id = db.Column(db.String(100), nullable=False, primary_key=True)
    serving_id = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "<Ingredient(meal='%d' food_id='%s', serving_id='%s', quantity='%f')>"%(self.meal, self.food_id, self.serving_id, self.quantity)
