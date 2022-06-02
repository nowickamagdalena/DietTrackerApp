import json
import datetime
from app import calorieCounter
from .searchService import SearchService
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Meal, Ingredient, User
from .__init__ import db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

diet_tracker = Blueprint('diet_tracker', __name__)
api = SearchService()
calCounter = calorieCounter.CalorieCounter(api)

@diet_tracker.route('/diet-tracker')
@login_required
def diet():
    return render_template('tracker.html')


#function redirection to food detail view
@diet_tracker.route('/diet-tracker/pickFoodDetails')
@login_required
def pickFoodDetails():   

    mealid = request.args.get('mealid')
    date = request.args.get('date')
    foodid = request.args.get('foodid')
    update = request.args.get('update')
    mealtype = request.args.get('mealtype')
    foodname = request.args.get('foodname')
    
    result = api.getFoodById(foodid)
    servings = result['servings']['serving']
    if type(servings) != list:
        result['servings']['serving'] = [servings]
        servings = [servings]
        
    #getting ingredent from database
    ingr = Ingredient.query.filter_by(meal=mealid, food_id=foodid).first()
    #getting all servings for given food
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

#function for counting calories for given food, serving and quantity
@diet_tracker.route('/diet-tracker/preview-calories')
@login_required
def countPreviewCalories():
    foodid = request.args.get('foodid')
    servingid = request.args.get('servingid')
    quantity = request.args.get('quantity')

    result = calCounter.calcNutrientsForServing(foodid, servingid, float(quantity))
    return json.dumps(result)

#function for adding food to meal
@diet_tracker.route('/diet-tracker/addFood', methods=['POST'])
@login_required
def addFood():
    mealid = request.form.get('mealid')
    foodid = request.form.get('foodid')
    foodname = request.form.get('foodname')
    servingid = request.form.get('servingid')
    quantity = request.form.get('quantity')
    date = request.form.get('date')
    update = request.form.get('update')
    mealtype=request.form.get('mealtype')

    #check if serving has been selected and display message otherwise
    if servingid == None:
        flash("Please select serving")
        return redirect(url_for("diet_tracker.pickFoodDetails", mealid=mealid, date=date, foodid=foodid, update=update, mealtype=mealtype, foodname=foodname))
    #check if quantity has been selected and display message otherwise
    if quantity == "":
        flash("Please select quantity")
        return redirect(url_for("diet_tracker.pickFoodDetails", mealid=mealid, date=date, foodid=foodid, update=update, mealtype=mealtype, foodname=foodname))

    food = Ingredient.query.filter_by(meal=mealid, food_id=foodid).first()

    if food:
        #if food of this id exist in this meal and it is not and update display message and redirect to meal
        if update =="false":
            flash("This ingredient has already been added to your meal, try different one, or change quantity of existing ingredient")
            return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date, mealtype=mealtype))
        else:
            #update ingredient data
            food.serving_id = servingid
            food.quantity = quantity
            db.session.commit()
    else:
        #create new ingredient object
        new_ing = Ingredient(meal=mealid, food_id=foodid, serving_id=servingid, quantity=quantity)
        db.session.add(new_ing)
        db.session.commit()
    return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date, mealtype=mealtype))

#function return search results to foodSearcher
@diet_tracker.route('/diet-tracker/search', methods=["GET"])
@login_required
def search():
    foodName = request.args.get('foodName')
    mealtype = request.args.get('mealtype')
    mealid = request.args.get('mealid')
    date = request.args.get('date')
    update = request.args.get('update')

    results = api.searchFood(foodName)

    return render_template("foodSearcher.html", foods=results, date=date, mealtype=mealtype, mealid=mealid, update=update)

#function displaying search window
@diet_tracker.route('/diet-tracker/searchFood', methods=['POST'])
@login_required
def searchFood():
    date = request.form.get('date')
    mealid = request.form.get('mealid')
    mealtype = request.form.get('mealtype')
    update = request.form.get('update')

    return render_template("foodSearcher.html", date=date, mealtype=mealtype, mealid=mealid, foods="false", update=update)
    
#function displaying meal choice for user
@diet_tracker.route('/newMeal')
@login_required
def newMeal():
    date = request.args.get('date')
    date_list=date.split("-")
    meals = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))).all()

    mealtypes = ["Breakfast", "Lunch", "Dinner", "Others"]
    existing = []
    #if given mealtype exists on this day, add it to list
    for meal in meals:
        existing.append(meal.type)
        
    return render_template("mealTypeChoice.html", date=date, existing=existing, mealtypes=mealtypes)

#function for adding new meals to database
@diet_tracker.route('/addMeal')
@login_required
def addMeal():
    date = request.args.get('date')
    date_list = date.split("-")
    mealtype = request.args.get('type')
    update = request.args.get('update')

    meal = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2])), type=mealtype).first()

    # check if the meal of given type already exists, shouldn't happen because buttons are disabled if added
    if meal:
        flash("Cannot add two meals of the same type")
        return redirect(url_for("diet_tracker.newMeal", date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))))

    #adding meal to database
    new_meal = Meal(type=mealtype, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2])), user=current_user.id)
    db.session.add(new_meal)
    db.session.commit()
    
    return render_template("foodSearcher.html", foods="false", date=new_meal.date, mealtype=mealtype, mealid=new_meal.id, update=update)


@diet_tracker.route('/diet-tracker/day', methods=["GET"])
@login_required
def getMealsForDay():
    date = request.args.get('date')

    mealOrder = {"Breakfast": 1, "Lunch": 2, "Dinner": 3, "Others": 4}

    #if user didn't specify date, display message and try again
    if date == '':
        flash("Pick the date from the calendar first")
        return redirect(url_for("diet_tracker.diet"))

    date_list = date.split("-")
    #get all the meals from database and sort them by type
    meals = Meal.query.filter_by(user=current_user.id, date=datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))).all()
    meals.sort(key=lambda meal: mealOrder[meal.type])

    # get nutrients for day and al meals
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
    percents = {'protein': 0, 'fat': 0, 'carbs': 0}
    colors = ['#94D22E', '#FDC40A', '#FF533F']
    if sum(nutrients) > 0:
        all = sum(nutrients)
        plt.figure().clear()
        plt.close()
        plt.cla()
        plt.clf()
        plt.pie(nutrients, labels = labels, startangle = 90, shadow=True, autopct=lambda x: '{:.2f}%'.format(x), colors=colors, wedgeprops = { 'linewidth' : 3, 'edgecolor' : 'white' })
        plt.axis('equal')
        plt.savefig('app/static/images/dailyChart.png', transparent=True)

        protein_pct = '{:.2f}%'.format(round(float(protein)/all*100, 2))
        fat_pct = '{:.2f}%'.format(round(float(fat)/all*100, 2))
        carbs_pct = '{:.2f}%'.format(round(float(carbs)/all*100, 2))
        fat = '{:.2f}'.format(round(float(fat),2))
        protein = '{:.2f}'.format(round(float(protein), 2))
        carbs = '{:.2f}'.format(round(float(carbs), 2))
        calories = int(round(float(calories)))
        percents = {'protein': protein_pct, 'fat': fat_pct, 'carbs': carbs_pct}
        
    return render_template('dailyStatistics.html', calories=calories, protein=protein, fat=fat, carbs=carbs, goals=userGoals, img_url="images/dailyChart.png", date=date, percents=percents)

#function displaying meal and its ingredients
@diet_tracker.route('/diet-tracker/meal')
@login_required
def getIngredientsForMeal():
    mealid = request.args.get("mealid")
    date = request.args.get("date")

    #get meal and its ingredients
    meal = Meal.query.filter_by(id=mealid).first()
    ingredients = Ingredient.query.filter_by(meal=mealid).all()
    food_list =[]

    #get all ingredients info from api
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

#function displaying meal statistics
@diet_tracker.route('/diet-tracker/<date>/<mealtype>/statistics', methods=["POST"])
@login_required
def mealStatistics(mealtype, date):
    calories = request.form.get("calories")
    protein = request.form.get("protein")
    fat = request.form.get("fat")
    carbs = request.form.get("carbs")
    mealid = request.form.get("mealid")
    
    #get user nutritional goals
    user = User.query.filter_by(id=current_user.id).first()
    userGoals = {"calories" : user.dailyCalGoal, "protein" : user.proteinPercentGoal, "fat" : user.fatPercentGoal, "carbs" : user.carbsPercentGoal}
        
    nutrients = [float(protein), float(fat), float(carbs)]
    labels = ["Protein", "Fat", "Carbohydrates"]
    percents = {'protein': 0, 'fat': 0, 'carbs': 0}
    colors = ['#94D22E', '#FDC40A', '#FF533F']

    if sum(nutrients) > 0:
        #create pie chart
        all = sum(nutrients)
        plt.figure().clear()
        plt.close()
        plt.cla()
        plt.clf()
        plt.pie(nutrients, labels = labels, startangle = 90, shadow=True, autopct=lambda x: '{:.2f}%'.format(x), colors=colors, wedgeprops = { 'linewidth' : 3, 'edgecolor' : 'white' })
        plt.axis('equal')
        plt.savefig('app/static/images/mealChart.png', transparent=True)

        protein_pct = '{:.2f}%'.format(round(float(protein)/all*100, 2))
        fat_pct = '{:.2f}%'.format(round(float(fat)/all*100, 2))
        carbs_pct = '{:.2f}%'.format(round(float(carbs)/all*100, 2))
        fat = '{:.2f}'.format(round(float(fat),2))
        protein = '{:.2f}'.format(round(float(protein), 2))
        carbs = '{:.2f}'.format(round(float(carbs), 2))
        calories = int(round(float(calories)))

        percents = {'protein': protein_pct, 'fat': fat_pct, 'carbs': carbs_pct}
    
    return render_template('mealStatistics.html', mealid=mealid, mealtype=mealtype, calories=calories, protein=protein, fat=fat, carbs=carbs, goals=userGoals, img_url="images/mealChart.png", date=date, percents=percents)

#function for deleting ingredient from database
@diet_tracker.route('/diet-tracker/deleteIngredient')
@login_required
def deleteIngredient():
    foodid = request.args.get('foodid')
    mealid = request.args.get('mealid')
    date = request.args.get('date')

    Ingredient.query.filter_by(meal=mealid, food_id=foodid).delete()
    db.session.commit()

    return redirect(url_for("diet_tracker.getIngredientsForMeal", mealid=mealid, date=date))

#function for displaying deleting confirmation window
@diet_tracker.route('/diet-tracker/confirm-delete-meal')
@login_required
def confirmDeleteMealOfId():
    mealtype = request.args.get('mealtype')
    mealid = request.args.get('mealid')
    date = request.args.get('date')

    return render_template('confirmDeleteWindow.html',mealid=mealid, mealtype=mealtype, date=date)

#function for deleting meal and its ingredients from database
@diet_tracker.route('/diet-tracker/deleteMeal')
@login_required
def deleteMealOfId():
    date = request.args.get('date')
    mealid = request.args.get('mealid')

    Meal.query.filter_by(id=mealid).delete()
    Ingredient.query.filter_by(meal=mealid).delete()
    db.session.commit()

    return redirect(url_for("diet_tracker.getMealsForDay", date=date))
