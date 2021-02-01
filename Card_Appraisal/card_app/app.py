

# used to import flask ... the render_template is used to render html
from flask import Flask, render_template, request, redirect

from flask_mysqldb import MySQL
app = Flask(__name__)




# basic route and the handler
@app.route("/")
def main():

    # we return the template html page called index
    return render_template('home.html')



#route from signup to home
@app.route('/showHome')
def showHome():
    return render_template('home.html')

@app.route('/actionpage')
def actionpage():
    return render_template('actionpage.html')






if __name__ == "__main__":
    #degug=true to auto dectect code change
    app.run(debug=True)