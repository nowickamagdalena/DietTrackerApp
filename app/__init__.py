from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    from .models import User

    #function will be called before every request to check user id in current session
    @login_manager.user_loader
    def load_user(user_id):        
        return User.query.get(int(user_id))

    # blueprint for auth routes 
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for main redirects
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for profile page routes
    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)

    # blueprint for diet tracker routes
    from .diet_tracker import diet_tracker as diet_blueprint
    app.register_blueprint(diet_blueprint)

    return app

