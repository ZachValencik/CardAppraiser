#import secrets,os
from PIL import Image # this is so we can resize the images so it doesnt take up a lot of sapce if its from a large image
from flask import render_template,url_for,flash,redirect,request,abort,session
from pokemon import app,bcrypt,mysql
#from pokemon.models import User
#from pokemon.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestRestForm,ResetPasswordForm
#from flask_login import login_user,current_user,logout_user,login_required
#from flask_mail import Message


@app.route('/')
@app.route('/home') # how to make two routes work on same page
def home():
  if "user" in session:
    user = session["user"]
    return render_template('home.html',userName=user)
  else: 
    return render_template('home.html')




@app.route('/register',methods=['GET','POST']) # need [methods=['GET','POST'] in able to use to submit data
def register():
  if request.method == 'POST':
    userDetails = request.form
    name = userDetails['name']
    email = userDetails['email']
    if userDetails['password'] != userDetails['checkpassword']:
          #return 'Passwords DontMatch', 400
          flash(f'Passwords dont match!','success')
          return render_template('register.html',title='register'),400
    else:
      try:
        hashed_password= bcrypt.generate_password_hash(userDetails['password']).decode('utf-8') # creating a hashed pw 
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO User(username,email,password) VALUES(%s,%s,%s)",(name,email,hashed_password))
        mysql.connection.commit()
        cur.close()
        flash(f'Your account has been created!','success') # A flash method that alerts the user that the form was completed
        return render_template('register.html',title='register'),200
      except:
        flash(f'ERROR!','success') # A flash method that alerts the user that the form was completed
        return render_template('register.html',title='register'),400

  return render_template('register.html',title='register')




@app.route('/login',methods=['GET','POST'])
def login():

  if request.method == "POST":
    #TO DO: Make it so it conncets to mysql and checks username and pw
    user = request.form["name"] 
    password = request.form["password"]
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM User WHERE username = %s""", (user,))
    

    mysql.connection.commit()
    userN = cur.fetchone()

    if userN == None: #This triggers if they enter a wrong username
      flash(f'Wrong username or password!','success')
      return render_template('login.html',title='login'),400

    cur.close()
    if(bcrypt.check_password_hash(userN['password'],password)): #Checks if it returns the user
      session["user"] = user # This should only pass if user and pw are correct
      return render_template('home.html',userName=user),200
    else:
      flash(f'Wrong username or password!','success')
      return render_template('login.html',title='login'),400
  else:
    return render_template('login.html',title='login'),400

@app.route('/logout')
def logout():
    session.pop('user',None)
    return render_template('home.html')


#route from signup to PokemonHome
@app.route('/PokemonHome',methods=['GET','POST'])
def PokemonHome():
  if "user" in session: # if user is logged in it will render the pokemon cards, otherwise redirect to login
    user = session["user"]
    return render_template('PokemonHome.html',title='PokemonHome')
  else:
    return render_template('login.html',title='login')



@app.route('/profile',methods=['GET','POST'])
def profile():
    user = session["user"]
    return render_template('profile.html',userName=user)
  

