from flask import Blueprint, render_template
from flask_login import current_user, login_required
from .models import Meal, Ingredient
from datetime import datetime, date
from .__init__ import db, create_app

diet_tracker = Blueprint('diet_tracker', __name__)


@diet_tracker.route('/diet-tracker')
@login_required
def diet():
    return render_template('calendar.html')

@diet_tracker.route('/diet-tracker/addmeal')
@login_required
def addMeal():
    new_meal = Meal(type="B", date=date(2020, 12, 6), user=current_user.id)
    print(new_meal.id)    
    db.session.add(new_meal)
    db.session.commit()
    new_ingredient = Ingredient(meal=new_meal.id, food_id='794', serving_id='733', quantity=1)
    next_ingredient = Ingredient(meal=new_meal.id, food_id='795', serving_id='733', quantity=1)
    db.session.add(new_ingredient)
    db.session.add(next_ingredient)
    db.session.commit()
    return render_template('calendar.html')

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
