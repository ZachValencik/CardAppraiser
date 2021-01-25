from flask import render_template,url_for,flash,redirect,request
from blogpost import app,db,bcrypt
from blogpost.models import User, Post
from blogpost.forms import RegistrationForm,LoginForm
from flask_login import login_user,current_user,logout_user,login_required

posts = [{  #Dummy Data for practice
  'author': 'corey schafer',
  'title': 'Blog post 1',
  'content':'First post content',
  'date_posted': 'April 20, 2018'
},
{
  'author': 'Jane DOe',
  'title': 'Blog post 2',
  'content':'Second post content',
  'date_posted': 'April 21, 2018'
}
]

@app.route('/')
@app.route('/home') # how to make two routes work on same page
def home():
    return render_template('home.html',posts=posts)


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


@app.route('/account')
@login_required # we need to login to use account
def account():
  return render_template('account.html',title='account')