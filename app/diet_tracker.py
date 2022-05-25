import datetime
import json
from .searchService import api
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Meal, Ingredient
from datetime import date
from .__init__ import db, create_app

diet_tracker = Blueprint('diet_tracker', __name__)


@diet_tracker.route('/diet-tracker')
@login_required
def diet():
    return render_template('tracker.html')


@diet_tracker.route('/diet-tracker/search')
@login_required
def searchFood():
    foodName = request.args.get('foodName')
    results = api.searchFood(foodName)
    return render_template("foodSearcher.html", foods=results)

@diet_tracker.route('/diet-tracker/searchById/<foodId>')
@login_required
def searchFoodId(foodId):
    results = api.getFoodById(foodId)
    return results

# @diet_tracker.route('/diet-tracker/addmeal')
# @login_required
# def addMeal():
#     new_meal = Meal(type="B", date=date(2020, 12, 6), user=current_user.id)
#     print(new_meal.id)    
#     db.session.add(new_meal)
#     db.session.commit()
#     new_ingredient = Ingredient(meal=new_meal.id, food_id='794', serving_id='733', quantity=1)
#     next_ingredient = Ingredient(meal=new_meal.id, food_id='795', serving_id='733', quantity=1)
#     db.session.add(new_ingredient)
#     db.session.add(next_ingredient)
#     db.session.commit()
#     return render_template('profile.html')



@diet_tracker.route('/newMeal/<date>')
def newMeal(date):
    # date = date.split("-")
    return render_template("mealTypeChoice.html", date=date)
    
@diet_tracker.route('/newMeal/<date>/<mealtype>')
def addMeal(mealtype, date):    
    date = date.split("-")
    meal = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date[0]),int(date[1]),int(date[2])), type=mealtype).first()

    # check if the meal of given type already exists
    if meal:
        flash("Cannot add two meals of the same type")
        return render_template("mealTypeChoice.html", date=datetime.date(int(date[0]),int(date[1]),int(date[2])))

    return render_template("foodSearcher.html", foods=None)


@diet_tracker.route('/diet-tracker/myDay', methods=["POST"])
@login_required
def getMealsForDay():
    date = request.form.get("date").split("-")
    meals = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date[0]),int(date[1]),int(date[2]))).all()
    meal_list =[]
    for meal in meals:
        meal_list.append({'id' : meal.id, 'type' : meal.type})
    print(meal_list)
    return render_template('dayView.html', date=datetime.date(int(date[0]),int(date[1]),int(date[2])), meals=meals)

@diet_tracker.route('/getIngredientsForMeal/<mealid>/<date>')
@login_required
def getIngredientsForMeal(mealid, date):
    # meal = request.form.get("mealid")
    ingredients = Ingredient.query.filter_by(meal=mealid).all()
    food_list =[]
    for ing in ingredients:
        food_details = api.getFoodById(ing.food_id)
        for s in food_details['servings']['serving']:
            if s['serving_id'] == ing.serving_id:
                s_name = s['serving_description']
        food_list.append({'foodid' : ing.food_id, 'name': food_details['food_name'], 'servingid' : ing.serving_id, 's_name':s_name, 'quantity' : ing.quantity})
    # print(food_list)
    return render_template('mealView.html', date=date, meals=mealid, foods=food_list)



def displayMealOfUserAndDate(user, date):
    app = create_app()
    with app.app_context():
        #date must be in datetime format
        meal = Meal.query.filter_by(user=user, date=date).all()
        return meal

def deleteMealOfId(id):
    app = create_app()
    with app.app_context():
        meal = Meal.query.filter_by(id=id).delete()
        ingredients = Ingredient.query.filter_by(meal=id).delete()
        db.session.commit()
        return meal, ingredients

# print(displayMealOfUserAndDate(2, datetime(2020,12,5)))
# deleteMealOfId(6)
