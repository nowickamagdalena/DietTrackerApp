from flask import Blueprint, render_template
from flask_login import current_user, login_required
from .__init__ import db
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, calories=current_user.dailyCalGoal, protein=current_user.proteinPercentGoal, fat=current_user.fatPercentGoal, carbs=current_user.carbsPercentGoal)

