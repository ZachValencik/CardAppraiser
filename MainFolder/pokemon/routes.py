#import secrets,os
import os
from PIL import Image # this is so we can resize the images so it doesnt take up a lot of sapce if its from a large image
from flask import render_template,url_for,flash,redirect,request,abort,session
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from pokemon import app,bcrypt,mysql
from werkzeug.utils import secure_filename 
UPLOAD_FOLDER = './pokemon/static/profile_pics'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#from pokemon.models import User
#from pokemon.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestRestForm,ResetPasswordForm
#from flask_login import login_user,current_user,logout_user,login_required
#from flask_mail import Message
s = URLSafeTimedSerializer('ThisisaSecret!')
app.config.from_pyfile('config.cfg')
mail = Mail(app)

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
    if len(name)<=0:
      flash(f'Must Enter a username','danger')
      return render_template('register.html',title='register'),400

    email = userDetails['email']
    if userDetails['password'] != userDetails['checkpassword']:
          #return 'Passwords DontMatch', 400
          flash(f'Passwords dont match!','danger')
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
        flash(f'ERROR!','danger') # A flash method that alerts the user that the form was completed
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
      flash(f'Wrong username or password!','danger')
      return render_template('login.html',title='login'),400

    cur.close()
    if(bcrypt.check_password_hash(userN['password'],password)): #Checks if it returns the user
      session["user"] = user # This should only pass if user and pw are correct
      return redirect(url_for('home'))
    else:
      flash(f'Wrong username or password!','danger')
      return render_template('login.html',title='login'),400
  else:
    return render_template('login.html',title='login'),400

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('home'))


#route from signup to PokemonHome
@app.route('/PokemonHome',methods=['GET','POST'])
def PokemonHome():
  if "user" in session: # if user is logged in it will render the pokemon cards, otherwise redirect to login
    user = session["user"]
    return render_template('PokemonHome.html',title='PokemonHome')
  else:
    return redirect(url_for('login'))



@app.route('/profile',methods=['GET','POST','DELETE'])
def profile():
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      cur.execute("""SELECT * FROM SocialMedia WHERE username = %s""", (user,))
      dataMediaPosts = cur.fetchall()
      return render_template('profile.html',userName=user,dataMediaPosts=dataMediaPosts)
    else:
      return redirect(url_for('login'))

@app.route('/editPost/<id>',methods=['GET','POST'])
def editPost(id):
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      sql = "Select * FROM SocialMedia WHERE post_id = %s and username = %s"
      adr = (int(id),user,)
      cur.execute(sql,adr)
      dataMediaPosts = cur.fetchall()
      if request.method == 'POST':
        print("In Here!!")
        mediaPost = request.form.get('message')
        image = request.files['img']
        cur = mysql.connection.cursor()
        sql = "Select * FROM SocialMedia WHERE post_id = %s and username = %s"
        adr = (int(id),user,)
        cur.execute(sql,adr)
        dataMediaPosts = cur.fetchall()

        if len(mediaPost) < 1:

          flash(f'Post must include more than 1 character','danger')
        else:
          cur = mysql.connection.cursor()
          if(image.filename==''):
             sql = "UPDATE SocialMedia Set post= %s WHERE post_id = %s and username = %s"
             adr = (mediaPost,int(id),user,)
             cur.execute(sql,adr)
          else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sql = "UPDATE SocialMedia Set post= %s, image= %s WHERE post_id = %s and username = %s"
            adr = (mediaPost,image.filename,int(id),user,)
            cur.execute(sql,adr)

          mysql.connection.commit()
          cur.close()
          flash(f'Your post was Updated','success') # A flash method that alerts the user that their post was completed
          #return render_template('socialMedia.html',title='Pokemon Forum', userName=user, dataMediaPosts=dataMediaPosts)
          return redirect(url_for('profile'))


      return render_template('editPost.html',userName=user, dataMediaPosts=dataMediaPosts)
    else:
      return redirect(url_for('login'))






#@app.route('/editPost/<id>',methods=['GET','PUT'])
#def editPost(id):
  #if "user" in session:
   # if request.method == "GET":
     # user = session["user"]
      #cur = mysql.connection.cursor()
     # sql = "Select * FROM SocialMedia WHERE post_id = %s and username = %s"
     # adr = (int(id),user,)
     # rows_count =cur.execute(sql,adr)
      #mysql.connection.commit()
     # if(rows_count ==0):
      #  cur.close()
       # flash(f'Not your post to edit!','danger')
       # return redirect(url_for('profile'))
     # else:  
        #dataMediaPosts = cur.fetchall()
      
        #cur.close()
       # return render_template('editPost.html',userName=user,dataMediaPosts=dataMediaPosts)
  #else:
    #return redirect(url_for('login'))

#@app.route('/putPost/<id>',methods=['GET','PUT'])
#def putPost(id):
  #if "user" in session:
  #    user = session["user"]
   #   print("PUT!!! "+ id)
    #  print(request.args.get('message'))
  #    cur = mysql.connection.cursor()
   #   sql = "UPDATE SocialMedia Set post= %s WHERE post_id = %s and username = %s"
   #   adr = (request.args.get('message'),int(id),user,)
   #   cur.execute(sql,adr)
   #   mysql.connection.commit()
    #  cur.close()
  #    return redirect(url_for('profile'))

      
  
    


@app.route('/deletePost/<id>',methods=['GET','DELETE'])
def deletePost(id):
  if "user" in session:
    print(id)
    user = session["user"]
    print(user)
    cur = mysql.connection.cursor()
    sql = "DELETE FROM SocialMedia WHERE post_id = %s and username = %s"
    adr = (int(id),user,)
    cur.execute(sql,adr)
    mysql.connection.commit()
    cur.close()
    flash(f'Post has been deleted','sucess')
    return redirect(url_for('profile'))
  else:
    return redirect(url_for('login'))
    




#@app.route('/profile/<username>',methods=['GET','POST'])
#def otherProfile(u):
  #  if "user" in session: 
   #   user = session["user"]
   #   if user == u:
   #     return render_template('profile.html',userName=user)
   #   else:
   #     cur = mysql.connection.cursor()
   #     cur.execute("""SELECT * FROM SocialMedia WHERE username = %s""", (u,))
  #      dataMediaPosts = cur.fetchall()
  #      return render_template('profile.html',dataMediaPosts=dataMediaPosts,u=u)
 #   else:
  #    return redirect(url_for('login'))  


@app.route('/social',methods=['GET','POST'])
def socialMedia():
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM SocialMedia")
      dataMediaPosts = cur.fetchall()
      if request.method == 'POST':
        mediaPost = request.form.get('mediaPost')
        image = request.files['img']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM SocialMedia")
        dataMediaPosts = cur.fetchall()

        if len(mediaPost) < 1:

          flash(f'Post must include more than 1 character','danger')
        else:
          cur = mysql.connection.cursor()
          if(image.filename==''):
            cur.execute("INSERT INTO SocialMedia(post,username) VALUES(%s,%s)",(mediaPost,user))
          else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            cur.execute("INSERT INTO SocialMedia(post,username,image) VALUES(%s,%s,%s)",(mediaPost,user,image.filename))
            
          

          mysql.connection.commit()
          cur.close()
          flash(f'Your post was published','success') # A flash method that alerts the user that their post was completed
          #return render_template('socialMedia.html',title='Pokemon Forum', userName=user, dataMediaPosts=dataMediaPosts)
          return redirect(url_for('socialMedia'))


      return render_template('socialMedia.html',userName=user, dataMediaPosts=dataMediaPosts)
    else:
      return redirect(url_for('login'))
  

@app.route('/forgotPassword',methods=['GET','POST'])
def forgotPassword():
  
  if "user" in session:
    user = session["user"]
    return redirect(url_for('home'))


  if request.method == "GET":
            return render_template('forgotPassword.html')
  email = request.form["email"]
  token = s.dumps(email)
  msg = Message('Reset Password ',sender="pokemoncardapp@gmail.com",recipients=[email])
  link = url_for('resetPassword',token=token,_external=True)
  msg.body= 'Your Link is {}'.format(link)
  mail.send(msg)

  flash("A password reset has been sent to your email ",'success')  
  return render_template('forgotPassword.html')


@app.route('/passwordReset/<token>',methods=['GET','POST'])
def resetPassword(token):

  try:
    email = s.loads(token,max_age=200)
  except SignatureExpired:
    flash("Token Expired")
    return redirect(url_for('forgotPassword'))

  if request.method == 'POST':
        hashed_password= bcrypt.generate_password_hash(request.form['password']).decode('utf-8') # creating a hashed pw 
        cur = mysql.connection.cursor()
        update = "UPDATE User SET password= '{}' WHERE email= '{}'".format(hashed_password,email)
        cur.execute(update)
        mysql.connection.commit()
        cur.close()
        flash(f'Your Password Has Been Updated','success') # A flash method that alerts the user that the form was completed
        return redirect(url_for('login'))

  return render_template('resetPassword.html')
      
        
