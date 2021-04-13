from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user
from flask_mail import Mail
from flask_mysqldb import MySQL,MySQLdb
from flask_mail import Mail,Message
#import yaml

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cards_S2021:cardsrOK!@45.55.136.114/cards_S2021'
app.config['SECRET_KEY'] = '10fe67da0b56b5384bd201830c37adf3' # import secrets secrets.token_hex(16)

#14-17 needed to log into the mysql server db 
app.config['MYSQL_HOST']= '45.55.136.114'
app.config['MYSQL_USER']= 'cards_S2021'
app.config['MYSQL_PASSWORD']= 'cardsrOK!'
app.config['MYSQL_DB']= 'cards_S2021'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
bcrypt = Bcrypt(app)
mysql = MySQL(app)


from pokemon import routes

