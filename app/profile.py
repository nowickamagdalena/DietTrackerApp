from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required
from .models import User
from .__init__ import db

profile = Blueprint('profile', __name__)

#function updating nutrition goals for user
@profile.route('/profile/updateGoals', methods=["POST"])
@login_required
def updateNutrients():
    calories = request.form.get("calories-limit")
    protein = request.form.get("protein-percent-goal")
    fat = request.form.get("fat-percent-goal")
    carbs = request.form.get("carbs-percent-goal")

    user = User.query.filter_by(id=current_user.id).first()

    #casting form data to numbers if given or None if empty 
    if calories == '':
        calories = None
    if fat != '':
        fatNum = int(fat)
    else:
        fatNum = 0
        fat = None
    if protein != '':
        proteinNum = int(protein)
    else:
        proteinNum = 0
        protein = None
    if carbs != '':
        carbsNum = int(carbs)
    else:
        carbsNum = 0
        carbs = None

    #if sum of percents is greater than 100 display message and let user try again
    if fatNum + proteinNum + carbsNum > 100:
        flash("Sum of your nutrients percentage cannot be greater than one hundred")
        return redirect(url_for("main.profile", name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal))
   
    #if all nutrients are given and sum of percents is not equal to 100 display message and let user try again
    if fat != None and protein != None and carbs != None and fatNum + proteinNum + carbsNum != 100:        
        flash("Sum of fat, protein and carbohydrates percentage must add up to one hundred")
        return redirect(url_for("main.profile", name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal))
   
    user.dailyCalGoal = calories
    user.proteinPercentGoal=protein
    user.fatPercentGoal = fat
    user.carbsPercentGoal = carbs
    db.session.commit()
    flash("Your goals have been updated successfully")

    return redirect(url_for("main.profile", name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal))
   

