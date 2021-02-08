import secrets,os
from PIL import Image # this is so we can resize the images so it doesnt take up a lot of sapce if its from a large image
from flask import render_template,url_for,flash,redirect,request,abort
from blogpost import app,db,bcrypt,mail
from blogpost.models import User
from blogpost.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestRestForm,ResetPasswordForm
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message

@app.route('/')
@app.route('/home') # how to make two routes work on same page
def home():
  return render_template('home.html',title="Home")


@app.route('/about')
def about():
    return render_template('about.html',title='The About')


@app.route('/register',methods=['GET','POST']) # need [methods=['GET','POST'] in able to use to submit data
def register():
  form = RegistrationForm()
  if current_user.is_authenticated:
    return redirect(url_for('home'))


  if form.validate_on_submit():
    hashed_password= bcrypt.generate_password_hash(form.password.data).decode('utf-8') # creating a hashed pw 
    user = User(username=form.username.data,email=form.email.data,password=hashed_password)
    db.session.add(user)
    db.session.commit()
    flash(f'Your account has been created!','success') # A flash method that alerts the user that the form was completed
    return redirect(url_for('login'))

  return render_template('register.html',title='register',form=form)




@app.route('/login',methods=['GET','POST'])
def login():
  if current_user.is_authenticated: # If already loggined in its goes to home page instead
    return redirect(url_for('home'))

  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password,form.password.data):
      login_user(user,remember=form.remember.data)
      next_page = request.args.get('next') #
      return redirect (next_page) if next_page else redirect(url_for('home'))
    else:
      flash('Login unsuccessful. please check email or password', 'danger')
  return render_template('login.html',title='login',form=form)


@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('home'))






def save_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _,f_ext = os.path.splitext(form_picture.filename)
  picture_fn = random_hex + f_ext
  picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)


  # this below code makes it so that the file size is only 125 by 25 pixels
  output_size = (125,125)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)

  return picture_fn





@app.route('/account',methods=['GET','POST'])
@login_required # we need to login to use account
def account():
  form = UpdateAccountForm()
  if form.validate_on_submit():
      if form.picture.data:
        picture_file = save_picture(form.picture.data)
        current_user.image_file = picture_file

      current_user.username = form.username.data
      current_user.email = form.email.data
      db.session.commit()
      flash('Your account has been updated','success')
      return redirect(url_for('account'))
  elif request.method == 'GET':
    form.username.data = current_user.username # populate form data with users info
    form.email.data = current_user.email



  image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
  return render_template('account.html',title='account',image_file=image_file,form=form)





def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestRestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

