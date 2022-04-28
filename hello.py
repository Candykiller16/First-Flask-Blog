from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a Flask Instance
app = Flask(__name__)
# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite"
# Secret Key
app.config['SECRET_KEY'] = 'This is my secret key'

db = SQLAlchemy(app)


# Model
class UsersModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name


# Users Form
class UserForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    email = StringField("Enter your email", validators=[DataRequired()])
    submit = SubmitField("Submit")


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
        flash("Form was submitted")
    return render_template('name.html',
                           name=name,
                           form=form)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    name = None
    email = None
    form = UserForm()
    # Validate Data form Form
    if form.validate_on_submit():
        user = UsersModel.query.filter_by(email=form.email.data).first()
        if user is None:
            user = UsersModel(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        email = form.email.data
        form.email.data = ""
        flash("User was added successfully")
    all_users = UsersModel.query.order_by(UsersModel.date_added)
    return render_template('add_user.html',
                           name=name,
                           email=email,
                           form=form,
                           all_users=all_users)

# Update User in Database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    user = UsersModel.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html', form=form, user=user)
        except:
            flash("Error! Try again")
            return render_template('update.html', form=form, user=user)
    else:
        return render_template('update.html', form=form, user=user)

