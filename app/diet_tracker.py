import json
from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required
from .models import Meal, Ingredient
import datetime
from .__init__ import db, create_app
from .searchService import api

diet_tracker = Blueprint('diet_tracker', __name__)


@diet_tracker.route('/diet-tracker')
@login_required
def diet():
    return render_template('calendar.html')

@diet_tracker.route('/diet-tracker/search/<foodName>')
@login_required
def searchFood(foodName):
    results = api.searchFood(foodName)
    return json.dumps(results)

@diet_tracker.route('/diet-tracker/searchById/<foodId>')
@login_required
def searchFoodId(foodId):
    results = api.getFoodById(foodId)
    return json.dumps(results)

@diet_tracker.route('/addmeal', methods=['POST'])
# @login_required must uncomment later
def addMeal():
    type = request.form.get("mealType")
    date = request.form.get("date").split("-")
    userid = request.form.get("userid")
    meal = Meal.query.filter_by(type=type, date=datetime.date(int(date[0]), int(date[1]), int(date[2])), user=int(userid)).first()
    if meal:
        flash("Cannot add two meals of the same type")
        return "False"
    new_meal = Meal(type=type, date=datetime.date(int(date[0]), int(date[1]), int(date[2])), user=int(userid))
    db.session.add(new_meal)
    db.session.commit()
    return new_meal.id

@diet_tracker.route('/addingredient', methods=['POST'])
# @login_required must uncomment later
def addIngredient():
    meal = request.form.get("mealid")
    food = request.form.get("foodid")
    serving = request.form.get("servingid")
    quantity = request.form.get("quantity")
    new_ingredient = Ingredient(meal=int(meal), food_id=food, serving_id=serving, quantity=float(quantity))
    db.session.add(new_ingredient)
    db.session.commit()
    return "test"

@diet_tracker.route('/getMealsForDay', methods=['POST'])
# @login_required must uncomment later
def getMealsForDay():
    date = request.form.get("date").split("-")
    meals = Meal.query.filter_by(user=2, date=datetime.date(int(date[0]),int(date[1]),int(date[2]))).all()
    json_list =[]
    for meal in meals:
        json_list.append({'id' : meal.id, 'type' : meal.type})
    print(json_list)
    return json.dumps(json_list)

@diet_tracker.route('/getIngredientsForMeal', methods=['POST'])
# @login_required must uncomment later
def getIngredientsForMeal():
    meal = request.form.get("mealid")
    ingredients = Ingredient.query.filter_by(meal=meal).all()
    json_list =[]
    for ing in ingredients:
        json_list.append({'foodid' : ing.food_id, 'servingid' : ing.serving_id, 'quantity' : ing.quantity})
    print(json_list)
    return json.dumps(json_list)

def displayMealsOfUserAndDate(user, date):
    app = create_app()
    with app.app_context():
        #date must be in datetime format
        meals = Meal.query.filter_by(user=user, date=date).all()
        return meals

@diet_tracker.route('/deleteMeal', methods=['POST'])
def deleteMealOfId():
    id = request.form.get("id")
    meal = Meal.query.filter_by(id=int(id)).delete()
    ingredients = Ingredient.query.filter_by(meal=int(id)).delete()
    db.session.commit()
    return "true"

