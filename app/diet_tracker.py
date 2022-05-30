import json
import datetime
import os
from app import calorieCounter
from .searchService import api
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Meal, Ingredient, User
from datetime import date
from .__init__ import db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

calCounter = calorieCounter.CalorieCounter(api)

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
    foodname = request.args.get('foodname')
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

    return render_template('foodDetails.html',mealid=mealid, mealtype=mealtype, date=date, food=result, serving=serving, quantity=quantity, update=update, foodname=foodname)

@diet_tracker.route('/diet-tracker/preview-calories')
@login_required
def countPreviewCalories():
    foodid = request.args.get('foodid')
    servingid = request.args.get('servingid')
    quantity = request.args.get('quantity')
    print(foodid, servingid, quantity)

    result = calCounter.calcNutrientsForServing(foodid, servingid, float(quantity))
    print(result)
    return json.dumps(result)



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
    date_list=date.split("-")
    meals = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))).all()
    mealtypes = ["Breakfast", "Lunch", "Dinner", "Others"]
    existing = []
    for meal in meals:
        existing.append(meal.type)
        
    return render_template("mealTypeChoice.html", date=date, existing=existing, mealtypes=mealtypes)

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
    date_list = date.split("-")
    mealtype = request.args.get('type')
    update = request.args.get('update')
    meal = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2])), type=mealtype).first()

    # check if the meal of given type already exists
    if meal:
        flash("Cannot add two meals of the same type")
        return redirect(url_for("diet_tracker.newMeal", date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))))

    new_meal = Meal(type=mealtype, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2])), user=current_user.id)
    db.session.add(new_meal)
    db.session.commit()
    
    return render_template("foodSearcher.html", foods=None, date=new_meal.date, mealtype=mealtype, mealid=new_meal.id, update=update)


@diet_tracker.route('/diet-tracker/myDay', methods=["GET"])
@login_required
def getMealsForDay():
    mealOrder = {"Breakfast": 1, "Lunch": 2, "Dinner": 3, "Others": 4}
    date = request.args.get('date')
    date_list = date.split("-")

    meals = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))).all()
    meals.sort(key=lambda meal: mealOrder[meal.type])

    nutrients = calCounter.calcNutrientsForDay(meals)

    return render_template('dayView.html', date=date, meals=meals, day_nutr=nutrients['day_sum'], meals_nutr=nutrients['meals_sum'])

@diet_tracker.route('/diet-tracker/<date>/statistics', methods=["POST"])
@login_required
def dayStatistics(date):
    calories = request.form.get("calories")
    protein = request.form.get("protein")
    fat = request.form.get("fat")
    carbs = request.form.get("carbs")
    
    user = User.query.filter_by(id=current_user.id).first()
    userGoals = {"calories" : user.dailyCalGoal, "protein" : user.proteinPercentGoal, "fat" : user.fatPercentGoal, "carbs" : user.carbsPercentGoal}
        
    nutrients = [float(protein), float(fat), float(carbs)]
    labels = ["Protein", "Fat", "Carbohydrates"]
    if sum(nutrients) > 0:
        plt.figure().clear()
        plt.close()
        plt.cla()
        plt.clf()
        plt.pie(nutrients, labels = labels, startangle = 90, shadow=True, autopct='%1.2f%%')
        plt.axis('equal')
        plt.savefig('app/static/images/dailyChart.png', transparent=True)
        
    return render_template('dailyStatistics.html', calories=calories, protein=protein, fat=fat, carbs=carbs, goals=userGoals, img_url="images/dailyChart.png", date=date)

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

    nutrients = calCounter.calcNutrientsForMeal(ingredients)

    return render_template('mealView.html', date=date, mealid=mealid, foods=food_list, mealtype=meal.type, meal_nutr=nutrients['meal_sum'], foods_nutr=nutrients['foods_sum'])

@diet_tracker.route('/diet-tracker/<date>/<mealtype>/statistics', methods=["POST"])
@login_required
def mealStatistics(mealtype, date):
    calories = request.form.get("calories")
    protein = request.form.get("protein")
    fat = request.form.get("fat")
    carbs = request.form.get("carbs")
    mealid = request.form.get("mealid")
    
    user = User.query.filter_by(id=current_user.id).first()
    userGoals = {"calories" : user.dailyCalGoal, "protein" : user.proteinPercentGoal, "fat" : user.fatPercentGoal, "carbs" : user.carbsPercentGoal}
        
    nutrients = [float(protein), float(fat), float(carbs)]
    labels = ["Protein", "Fat", "Carbohydrates"]
    
    if sum(nutrients) > 0:
        plt.figure().clear()
        plt.close()
        plt.cla()
        plt.clf()
        plt.pie(nutrients, labels = labels, startangle = 90, shadow=True, autopct='%1.2f%%')
        plt.axis('equal')
        plt.savefig('app/static/images/dailyChart.png', transparent=True)
    
    return render_template('mealStatistics.html', mealid=mealid, mealtype=mealtype, calories=calories, protein=protein, fat=fat, carbs=carbs, goals=userGoals, img_url="images/mealChart.png", date=date)

@diet_tracker.route('/diet-tracker/deleteIngredient')
@login_required
def deleteIngredient():
    foodid = request.args.get('foodid')
    mealid = request.args.get('mealid')
    date = request.args.get('date')

    Ingredient.query.filter_by(meal=mealid, food_id=foodid).delete()
    db.session.commit()

    return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date))

@diet_tracker.route('/diet-tracker/confirm-delete-meal')
@login_required
def confirmDeleteMealOfId():
    mealtype = request.args.get('mealtype')
    mealid = request.args.get('mealid')
    date = request.args.get('date')

    return render_template('confirmDeleteWindow.html',mealid=mealid, mealtype=mealtype, date=date)

@diet_tracker.route('/diet-tracker/deleteMeal/<mealid>')
@login_required
def deleteMealOfId(mealid):
    date = request.args.get('date')

    meal = Meal.query.filter_by(id=mealid).delete()
    ingredients = Ingredient.query.filter_by(meal=mealid).delete()
    db.session.commit()

    return redirect(url_for("diet_tracker.getMealsForDay", date=date))

# print(displayMealOfUserAndDate(2, datetime(2020,12,5)))
# deleteMealOfId(6)
