from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is my secret key'


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Home page
@app.route('/')
def index():
    first_name = 'Anton'
    pizzas = ['cheese', 'mushrooms', 'salami', 16]
    return render_template('index.html', first_name=first_name, pizzas=pizzas)


# User profile page
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# Page doesn't exist page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Server error
@app.errorhandler(500)
def server_problem(e):
    return render_template('500.html'), 500


# Name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Data form Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
    return render_template('name.html',
                           name=name,
                           form=form)
