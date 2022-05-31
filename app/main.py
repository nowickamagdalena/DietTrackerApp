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
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('profile.html', name=current_user.name, calories=user.dailyCalGoal, protein=user.proteinPercentGoal, fat=user.fatPercentGoal, carbs=user.carbsPercentGoal)

