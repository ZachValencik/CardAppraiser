from datetime import datetime
from blogpost import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model,UserMixin): # this is the user in the db
  
  id = db.Column(db.Integer,primary_key=True) #Each user id is unique with a priamry key
  username = db.Column(db.String(20),unique=True,nullable=False) # each username is unique and cant be nulll
  email = db.Column(db.String(20),unique=True,nullable=False)
  image_file = db.Column(db.String(20),nullable=False,default='default.jpg') 
  password = db.Column(db.String(60),nullable=False)
  posts = db.relationship('Post',backref='author',lazy=True)

  def __repr__(self): #how our object is printed when its printed out
    return f"User('{self.username},{self.email},{self.image_file}')"


class Post(db.Model): # how the post a user does is made in the db
  
  id = db.Column(db.Integer,primary_key=True) #Each user id is unique with a priamry key
  title =  db.Column(db.String(100),nullable=False)
  date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow) 
  content = db.Column(db.Text,nullable=False)
  user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) # Connecting user and post

  def __repr__(self):
    return f"Post('{self.title},{self.date_posted}')"