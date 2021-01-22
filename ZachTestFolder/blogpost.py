from flask import Flask, escape, request,render_template,url_for,flash,redirect
from forms import RegistrationForm,LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '10fe67da0b56b5384bd201830c37adf3' # import secrets secrets.token_hex(16)

posts = [{
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

  if form.validate_on_submit():
    flash(f'Account created for {form.username.data}!','success') # A flash method that alerts the user that the form was completed
    return redirect(url_for('home'))

  return render_template('register.html',title='register',form=form)




@app.route('/login',methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    if form.email.data == 'admin@blog.com' and form.password.data == 'password': #dummy data to see if it works
      flash('YOu have been logged in!','success')
      return redirect(url_for('home'))
    else:
      flash('Login unsuccessful. please check email or password', 'danger')
  return render_template('login.html',title='login',form=form)




#set FLASK_DEBUG=1
# How to run it in debug with just running it in python
if __name__ == '__main__':
  app.run(debug=True)
