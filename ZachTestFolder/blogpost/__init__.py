from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_manager
from flask_mail import Mail
app = Flask(__name__)
app.config['SECRET_KEY'] = '10fe67da0b56b5384bd201830c37adf3' # import secrets secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # needed for the user to not see the account page while not logged in
login_manager.login_message_category = 'info' # makes the flash messages look better

from blogpost import routes