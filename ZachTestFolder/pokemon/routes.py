#import secrets,os
from PIL import Image # this is so we can resize the images so it doesnt take up a lot of sapce if its from a large image
from flask import render_template,url_for,flash,redirect,request,abort
from pokemon import app,bcrypt,mysql
#from pokemon.models import User
#from pokemon.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestRestForm,ResetPasswordForm
#from flask_login import login_user,current_user,logout_user,login_required
#from flask_mail import Message


@app.route('/')
@app.route('/home') # how to make two routes work on same page
def home():
  return render_template('home.html',title="Home")




@app.route('/register',methods=['GET','POST']) # need [methods=['GET','POST'] in able to use to submit data
def register():
  if request.method == 'POST':

    userDetails = request.form
    name = userDetails['name']
    email = userDetails['email']
    if userDetails['password'] != userDetails['checkpassword']:
          flash(f'Passwords dont match!','success')
          return render_template('register.html',title='register')
    else:
      try:
        hashed_password= bcrypt.generate_password_hash(userDetails['password']).decode('utf-8') # creating a hashed pw 
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO User(username,email,password) VALUES(%s,%s,%s)",(name,email,hashed_password))
        mysql.connection.commit()
        cur.close()
        flash(f'Your account has been created!','success') # A flash method that alerts the user that the form was completed
        return render_template('register.html',title='register')
      except:
        flash(f'ERROR!','success') # A flash method that alerts the user that the form was completed
        return render_template('register.html',title='register')

  return render_template('register.html',title='register')




@app.route('/login',methods=['GET','POST'])
def login():

  return render_template('login.html',title='login')

#route from signup to PokemonHome
@app.route('/PokemonHome')
def PokemonHome():
    return render_template('PokemonHome.html',title='PokemonHome')


