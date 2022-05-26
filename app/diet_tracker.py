import datetime
import json
from turtle import update
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


@diet_tracker.route('/diet-tracker/pickFoodDetails/<mealid>/<date>/<foodid>')
@login_required
def pickFoodDetails(mealid, date, foodid):   

    update = request.args.get('update')
    mealtype = request.args.get('mealtype')
    print(update, mealtype)

    result = api.getFoodById(foodid)
    servings = result['servings']['serving']
    if type(servings) != list:
        result['servings']['serving'] = [servings]
        servings = [servings]
        
    ingr = Ingredient.query.filter_by(meal=mealid, food_id=foodid).first()
    if ingr:
        serving = None
        index = 0
        while serving == None and index < len(servings):
            if servings[index]['serving_id'] == ingr.serving_id:
                serving = servings[index]
            index +=1
        quantity = ingr.quantity
    else:
        serving = None
        quantity = None

    return render_template('foodDetails.html',mealid=mealid, mealtype=mealtype, date=date, food=result, serving=serving, quantity=quantity, update=update)

@diet_tracker.route('/diet-tracker/addFood', methods=['POST'])
@login_required
def addFood():
    mealid = request.form.get('mealid')
    foodid = request.form.get('foodid')
    servingid = request.form.get('servingid')
    quantity = request.form.get('quantity')
    date = request.form.get('date')
    update = request.form.get('update')
    mealtype=request.form.get('mealtype')
    print("serving id:", servingid)
    print(quantity, servingid)

    if servingid == None:
        flash("Please select serving")
        return redirect(url_for("diet_tracker.pickFoodDetails", mealid=mealid, date=date, foodid=foodid, update=update, mealtype=mealtype))
    if quantity == "":
        flash("Please select quantity")
        return redirect(url_for("diet_tracker.pickFoodDetails", mealid=mealid, date=date, foodid=foodid, update=update, mealtype=mealtype))

    # print(mealid, foodid, servingid, quantity,date)

    food = Ingredient.query.filter_by(meal=mealid, food_id=foodid).first()

    if food:
        if update =="false":
            flash("This ingredient has already been added to your meal, try different one, or change quantity of existing ingredient")
            return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date, mealtype=mealtype))
        else:
            food.serving_id = servingid
            food.quantity = quantity
            db.session.commit()
    else:
        new_ing = Ingredient(meal=mealid, food_id=foodid, serving_id=servingid, quantity=quantity)
        db.session.add(new_ing)
        db.session.commit()
    return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date, mealtype=mealtype))


@diet_tracker.route('/diet-tracker/search', methods=["GET"])
@login_required
def searchFood():
    foodName = request.args.get('foodName')
    mealtype = request.args.get('mealtype')
    mealid = request.args.get('mealid')
    date = request.args.get('date')
    update = request.args.get('update')
    print(mealtype)
    results = api.searchFood(foodName)
    return render_template("foodSearcher.html", foods=results, date=date, mealtype=mealtype, mealid=mealid, update=update)

@diet_tracker.route('/diet-tracker/searchById/<foodId>')
@login_required
def searchFoodId(foodId):
    results = api.getFoodById(foodId)
    return results

@diet_tracker.route('/newMeal/<date>')
def newMeal(date):
    # date = date.split("-")
    return render_template("mealTypeChoice.html", date=date)

@diet_tracker.route('/diet-tracker/searchIngredients', methods=['POST'])
def searchIngredients():
    date = request.form.get('date')
    mealid = request.form.get('mealid')
    mealtype = request.form.get('mealtype')
    update = request.form.get('update')
    print(update)
    return render_template("foodSearcher.html", date=date, mealtype=mealtype, mealid=mealid, foods=None, update=update)


@diet_tracker.route('/addMeal/<date>')
def addMeal(date):    
    date = date.split("-")
    mealtype = request.args.get('type')
    meal = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date[0]),int(date[1]),int(date[2])), type=mealtype).first()

    # check if the meal of given type already exists
    if meal:
        flash("Cannot add two meals of the same type")
        return redirect(url_for("diet_tracker.newMeal", date=datetime.date(int(date[0]),int(date[1]),int(date[2]))))

    new_meal = Meal(type=mealtype, date=datetime.date(int(date[0]),int(date[1]),int(date[2])), user=current_user.id)
    db.session.add(new_meal)
    db.session.commit()
    
    return render_template("foodSearcher.html", foods=None, date=new_meal.date, mealtype=mealtype, mealid=new_meal.id)


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
    meal = Meal.query.filter_by(id=mealid).first()
    ingredients = Ingredient.query.filter_by(meal=mealid).all()
    food_list =[]
    for ing in ingredients:
        food_details = api.getFoodById(ing.food_id)
        servings = food_details['servings']['serving']
        if type(servings) != list:
            servings = [servings]
        for s in servings:
            if s['serving_id'] == ing.serving_id:
                s_name = s['serving_description']
        food_list.append({'foodid' : ing.food_id, 'name': food_details['food_name'], 'servingid' : ing.serving_id, 's_name':s_name, 'quantity' : ing.quantity})
    # print(food_list)
    return render_template('mealView.html', date=date, mealid=mealid, foods=food_list, mealtype=meal.type)

@diet_tracker.route('/diet-tracker/deleteIngredient')
@login_required
def deleteIngredient():
    foodid = request.args.get('foodid')
    mealid = request.args.get('mealid')
    date = request.args.get('date')

    Ingredient.query.filter_by(meal=mealid, food_id=foodid).delete()
    db.session.commit()

    return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date))



def deleteMealOfId(id):
    app = create_app()
    with app.app_context():
        meal = Meal.query.filter_by(id=id).delete()
        ingredients = Ingredient.query.filter_by(meal=id).delete()
        db.session.commit()
        return meal, ingredients

# print(displayMealOfUserAndDate(2, datetime(2020,12,5)))
# deleteMealOfId(6)
