# import secrets,os
import MySQLdb

import datetime
import os
from PIL import \
    Image  # this is so we can resize the images so it doesnt take up a lot of sapce if its from a large image
from flask import render_template, url_for, flash, redirect, request, abort, session, jsonify
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from pokemon import app, bcrypt, mysql
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
dropzone = Dropzone(app)
UPLOAD2_FOLDER = './pokemon/static/uploads'
#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD2_FOLDER'] = UPLOAD2_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = './pokemon/static/profile_pics'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# from pokemon.models import User
# from pokemon.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestRestForm,ResetPasswordForm
# from flask_login import login_user,current_user,logout_user,login_required
# from flask_mail import Message
s = URLSafeTimedSerializer('ThisisaSecret!')
app.config.from_pyfile('config.cfg')
mail = Mail(app)


@app.route('/')
@app.route('/home') # how to make two routes work on same page
def home():
  if "user" in session:
    user = session["user"]
    if "admin" in session:
      admin = session["admin"]
      return render_template('home.html',userName=user,admin=admin)
    else:
      return render_template('home.html',userName=user)

  else: 
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])  # need [methods=['GET','POST'] in able to use to submit data
def register():
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        if len(name) <= 0:
            flash(f'Must Enter a username', 'danger')
            return render_template('register.html', title='register'), 400

        email = userDetails['email']
        if userDetails['password'] != userDetails['checkpassword']:
            # return 'Passwords DontMatch', 400
            flash(f'Passwords dont match!', 'danger')
            return render_template('register.html', title='register'), 400
        else:
            try:
                hashed_password = bcrypt.generate_password_hash(userDetails['password']).decode(
                    'utf-8')  # creating a hashed pw
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO User(username,email,password) VALUES(%s,%s,%s)",
                            (name, email, hashed_password))
                mysql.connection.commit()
                cur.close()
                flash(f'Your account has been created!',
                      'success')  # A flash method that alerts the user that the form was completed
                return redirect(url_for('login'))
            except:
                flash(f'ERROR!', 'danger')  # A flash method that alerts the user that the form was completed
                return render_template('register.html', title='register'), 400

    return render_template('register.html', title='register')


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
      if(userN['is_admin']==1):
        print("Logged in as an admin!")
        session["admin"] = userN['is_admin']
      else:
        print("Logged in as a regular user")
      return redirect(url_for('home'))
    else:
      flash(f'Wrong username or password!','danger')
      return render_template('login.html',title='login'),400
  else:
    return render_template('login.html',title='login'),200


@app.route('/logout')
def logout():
  session.pop('user', None)
  session.pop('admin',None)
  return redirect(url_for('home'))

# route from signup to PokemonHome
@app.route('/PokemonHome', methods=['GET', 'POST'])
def PokemonHome():
    if "user" in session:
        user = session["user"]
        if "admin" in session:
            admin = session["admin"]
            return render_template('PokemonHome.html', userName=user, admin=admin)
        else:
            return render_template('PokemonHome.html', userName=user)

    else:
        return render_template('PokemonHome.html')


# route from signup to myList
@app.route('/myList', methods=['GET', 'POST'])
def myList():
    if "user" in session:
        user = session["user"]
        if "admin" in session:
            admin = session["admin"]
            return render_template('myList.html', userName=user, admin=admin)
        else:
            return render_template('myList.html', userName=user)

    else:
        return render_template('myList.html')


# //


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == 'POST':
        user = session["user"]
        f= request.files.get('file')
        f.save(os.path.join(app.config['UPLOAD2_FOLDER'], f.filename))
        d1 = datetime.datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO uploads(file_name,user,upload_time) VALUES(%s,%s,%s)",
                            (f.filename,user,d1))
        mysql.connection.commit()
        cur.close()


    return render_template('myList.html')
  





@app.route('/profile',methods=['GET','POST','DELETE'])
def profile():
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      cur.execute("""SELECT * FROM SocialMedia WHERE username = %s""", (user,))
      dataMediaPosts = cur.fetchall()
      if "admin" in session:
        admin = session["admin"]
        return render_template('profile.html',userName=user,dataMediaPosts=dataMediaPosts,admin=admin)
      else:
        return render_template('profile.html',userName=user,dataMediaPosts=dataMediaPosts)

    else:
      return redirect(url_for('login'))

@app.route('/viewPost/<id>',methods=['GET','POST'])
def viewPost(id):
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      curComments = mysql.connection.cursor()
      if "admin" in session:
        sql = "SELECT * FROM SocialMedia WHERE post_id = %s" #grabs post from DB with post_id THIS WORKS
        #sql = "SELECT * FROM SocialMedia INNER JOIN SocialMediaComments ON SocialMedia.post_id = SocialMediaComments.post_id WHERE post_id = %s"
        #sql = "SELECT SocialMedia.post_id, SocialMedia.post, SocialMedia.username, SocialMedia.image, SocialMedia.time, SocialMediaComments.comment, SocialMediaComments.username, SocialMediaComments.image, SocialMediaComments.time FROM SocialMedia INNER JOIN SocialMediaComments ON SocialMedia.post_id = SocialMediaComments.post_id where SocialMedia.post_id = %s"
        sqlComments = "SELECT * FROM SocialMediaComments WHERE post_id = %s"
        adr = (int(id),)
      else:
        sql = "Select * FROM SocialMedia WHERE post_id = %s" #grabs post from DB with post_id THIS WORKS
        #sql = "SELECT * FROM SocialMedia INNER JOIN SocialMediaComments ON SocialMedia.post_id = SocialMediaComments.post_id WHERE post_id = %s"
        #sql = "SELECT SocialMedia.post_id, SocialMedia.post, SocialMedia.username, SocialMedia.image, SocialMedia.time, SocialMediaComments.comment, SocialMediaComments.username, SocialMediaComments.image, SocialMediaComments.time FROM SocialMedia INNER JOIN SocialMediaComments ON SocialMedia.post_id = SocialMediaComments.post_id where SocialMedia.post_id = %s"
        sqlComments = "SELECT * FROM SocialMediaComments WHERE post_id = %s"
        adr = (int(id),)
      cur.execute(sql,adr)
      curComments.execute(sqlComments,adr)

      #cur.execute("""SELECT * FROM SocialMedia WHERE post_id = %s""", (int(id),))
      dataMediaPosts = cur.fetchall()
      commentsMediaPosts = curComments.fetchall()

      if request.method == 'POST':
        commentPost = request.form.get('commentPost')
        image = request.files['img']
        curComments = mysql.connection.cursor()
        curComments.execute("SELECT * FROM SocialMediaComments")
        commentsMediaPosts = curComments.fetchall()

        if len(commentPost) < 1:
          flash(f'Post must include more than 1 character', 'danger')
        else:
          cur = mysql.connection.cursor()
          if(image.filename==''):
            cur.execute("INSERT INTO SocialMediaComments(comment,username,post_id) VALUES(%s,%s,%s)", (commentPost,user,adr))
          else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur.execute("INSERT INTO SocialMediaComments(comment,username,image,post_id) VALUES(%s,%s,%s,%s)",(commentPost,user,image.filename,adr))
          mysql.connection.commit()
          cur.close()
          flash(f'Your comment was published','success')
          return redirect(url_for('viewPost', id = id))
          #return redirect(url_for('viewPost/<id>'))
          #return render_template('viewPost.html',userName=user,dataMediaPosts=dataMediaPosts)
      if "admin" in session:
        admin = session["admin"]
        return render_template('viewPost.html',userName=user,dataMediaPosts=dataMediaPosts,commentsMediaPosts=commentsMediaPosts, admin=admin)
      else:
        return render_template('viewPost.html',userName=user,dataMediaPosts=dataMediaPosts, commentsMediaPosts=commentsMediaPosts)

    else:
      return redirect(url_for('login'))
    

@app.route('/displayMyList',methods=['GET','POST','DELETE'])
def displayMyList():
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      cur.execute("""SELECT * FROM uploads WHERE user = %s""", (user,))
      dataMediaPosts = cur.fetchall()
      if "admin" in session:
        admin = session["admin"]
        return render_template('displayMyList.html',userName=user,dataMediaPosts=dataMediaPosts,admin=admin)
      else:
        return render_template('displayMyList.html',userName=user,dataMediaPosts=dataMediaPosts)


@app.route('/editPost/<id>',methods=['GET','POST'])
def editPost(id):
    if "user" in session:
      user = session["user"]
      cur = mysql.connection.cursor()
      if "admin" in session:
        sql = "Select * FROM SocialMedia WHERE post_id = %s"
        adr = (int(id),)
      else:
        sql = "Select * FROM SocialMedia WHERE post_id = %s and username = %s"
        adr = (int(id),user,)
      cur.execute(sql,adr)
      dataMediaPosts = cur.fetchall()
      if request.method == 'POST':
       
        mediaPost = request.form.get('message')
        image = request.files['img']
        cur = mysql.connection.cursor()
        if "admin" in session:
          sql = "Select * FROM SocialMedia WHERE post_id = %s"
          adr = (int(id),)
        else:
          sql = "Select * FROM SocialMedia WHERE post_id = %s and username = %s"
          adr = (int(id),user,)
          cur.execute(sql,adr)
          dataMediaPosts = cur.fetchall()

        if len(mediaPost) < 1:

          flash(f'Post must include more than 1 character','danger')
        else:
          cur = mysql.connection.cursor()
          if(image.filename=='' or request.form.getlist('check')):
            if "admin" in session:
              if request.form.getlist('check'):
                sql = "UPDATE SocialMedia Set post= %s, image= %s WHERE post_id = %s"
                adr = (mediaPost,"",int(id),)
                cur.execute(sql,adr)
              else:
                sql = "UPDATE SocialMedia Set post= %s WHERE post_id = %s"
                adr = (mediaPost,int(id),)
                cur.execute(sql,adr)
            else:
              if request.form.getlist('check'):
                sql = "UPDATE SocialMedia Set post= %s, image= %s WHERE post_id = %s and username = %s"
                adr = (mediaPost,"",int(id),user,)
                cur.execute(sql,adr)
              else:
                sql = "UPDATE SocialMedia Set post= %s WHERE post_id = %s and username = %s"
                adr = (mediaPost,int(id),user,)
                cur.execute(sql,adr)

          else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if "admin" in session:
              sql = "UPDATE SocialMedia Set post= %s, image= %s WHERE post_id = %s"
              adr = (mediaPost,image.filename,int(id))
            else:
              sql = "UPDATE SocialMedia Set post= %s, image= %s WHERE post_id = %s and username = %s"
              adr = (mediaPost,image.filename,int(id),user,)
            cur.execute(sql,adr)

          mysql.connection.commit()
          cur.close()
          flash(f'Your post was Updated','success') # A flash method that alerts the user that their post was completed
          #return render_template('socialMedia.html',title='Pokemon Forum', userName=user, dataMediaPosts=dataMediaPosts)
          if "admin" in session:
            return redirect(url_for('admin'))
          else:
            return redirect(url_for('profile'))


      return render_template('editPost.html',userName=user, dataMediaPosts=dataMediaPosts)
    else:
      return redirect(url_for('login'))



@app.route('/deletePost/<id>', methods=['GET', 'DELETE'])
def deletePost(id):
    if "user" in session:
        print(id)
        user = session["user"]
        print(user)
        cur = mysql.connection.cursor()
        sql = "DELETE FROM SocialMedia WHERE post_id = %s and username = %s"
        adr = (int(id), user,)
        cur.execute(sql, adr)
        mysql.connection.commit()
        cur.close()
        flash(f'Post has been deleted', 'sucess')
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))

@app.route('/deletePost2/<id>', methods=['GET', 'DELETE'])
def deletePost2(id):
    if "user" in session:
        print(id)
        user = session["user"]
        print(user)
        cur = mysql.connection.cursor()
        sql = "DELETE FROM uploads WHERE upload_id = %s and user = %s"
        adr = (int(id), user,)
        cur.execute(sql, adr)
        mysql.connection.commit()
        cur.close()
        flash(f'Post has been deleted', 'sucess')
        return redirect(url_for('displayMyList'))
    else:
        return redirect(url_for('login'))


@app.route('/admin',methods=['GET','POST','PUT','DELETE'])
def admin():
    if "user" in session:
      user = session["user"]
      if "admin" in session:

        admin = session["admin"]
        cur = mysql.connection.cursor()
        cur.execute("""SELECT * FROM SocialMedia""")
        dataMediaPosts = cur.fetchall()
        return render_template('admin.html',userName=user,dataMediaPosts=dataMediaPosts,admin=admin)
      else:
        return redirect(url_for('home'))
    else:
      return redirect(url_for('login'))

@app.route('/socialMedia',methods=['GET','POST','PUT','DELETE'])
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
      if "admin" in session:
       admin = session["admin"]
       return render_template('socialMedia.html',userName=user, dataMediaPosts=dataMediaPosts,admin=admin)
      else:
        return render_template('socialMedia.html',userName=user, dataMediaPosts=dataMediaPosts)

    else:
      return redirect(url_for('login'))


@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if "user" in session:
        user = session["user"]
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template('forgotPassword.html')
    email = request.form["email"]
    token = s.dumps(email)
    msg = Message('Reset Password ', sender="pokemoncardapp@gmail.com", recipients=[email])
    link = url_for('resetPassword', token=token, _external=True)
    msg.body = 'Your Link is {}'.format(link)
    mail.send(msg)

    flash("A password reset has been sent to your email ", 'success')
    return render_template('forgotPassword.html')


@app.route('/passwordReset/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    try:
        email = s.loads(token, max_age=200)
    except SignatureExpired:
        flash("Token Expired")
        return redirect(url_for('forgotPassword'))

    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode(
            'utf-8')  # creating a hashed pw
        cur = mysql.connection.cursor()
        update = "UPDATE User SET password= '{}' WHERE email= '{}'".format(hashed_password, email)
        cur.execute(update)
        mysql.connection.commit()
        cur.close()
        flash(f'Your Password Has Been Updated',
              'success')  # A flash method that alerts the user that the form was completed
        return redirect(url_for('login'))

    return render_template('resetPassword.html')
