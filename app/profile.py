from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user, login_required
from .models import User
from .__init__ import db

# dailyCalGoal = db.Column(db.Integer)
#     proteinPercentGoal = db.Column(db.Integer)
#     fatPercentGoal = db.Column(db.Integer)
#     carbsPercentGoal = db.Column(db.Integer)

profile = Blueprint('profile', __name__)

@profile.route('/profile/updateGoals', methods=["POST"])
@login_required
def updateNutrients():
    calories = request.form.get("calories-limit")
    protein = request.form.get("protein-percent-goal")
    fat = request.form.get("fat-percent-goal")
    carbs = request.form.get("carbs-percent-goal")

    user = User.query.filter_by(id=current_user.id).first()
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

    if fatNum + proteinNum + carbsNum > 100:
        flash("Sum of your nutrients percentage cannot be grater than one hundred")
        return render_template("profile.html", name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal)
    if fat != None and protein != None and carbs != None and fatNum + proteinNum + carbsNum != 100:        
        flash("Sum of fat, protein and carbohydrates percentage must add up to one hundred")
        return render_template("profile.html", name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal)

    user.dailyCalGoal = calories
    user.proteinPercentGoal=protein
    user.fatPercentGoal = fat
    user.carbsPercentGoal = carbs
    db.session.commit()
    flash("Your goals have been updated successfully")

    return render_template("profile.html", name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal)


