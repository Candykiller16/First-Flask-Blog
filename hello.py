from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

# Create a Flask Instance
app = Flask(__name__)
# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite"
# Secret Key
app.config['SECRET_KEY'] = 'This is my secret key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Posts Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(255))
    slug = db.Column(db.String(255))


# Post Form
class PostForm(FlaskForm):
    title = StringField("Enter title", validators=[DataRequired()])
    content = StringField("Enter content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Enter author", validators=[DataRequired()])
    slug = StringField("Enter slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# All posts
@app.route('/posts')
def posts():
    posts = Posts.query.order_by('date_added')
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('single-post.html', post=post)


# Add Post
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit:
        # Submit Form
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     author=form.author.data,
                     slug=form.slug.data)
        # Clear Form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # Add post to database
        db.session.add(post)
        db.session.commit()
        flash('Post was successfully added')
    return render_template('add_post.html', form=form)


# Users Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    favourite_color = db.Column(db.String(200))
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(200))

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name


# Users Form
class UserForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    email = StringField("Enter your email", validators=[DataRequired()])
    favourite_color = StringField("Enter your favourite color", validators=[DataRequired()])
    password_hash = PasswordField("Enter your password", validators=[DataRequired(),
                                                                     EqualTo('password_hash2',
                                                                             message='Passwords Must Match')])
    password_hash2 = PasswordField("Submit your password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's your email?", validators=[DataRequired()])
    password = PasswordField("What's your password?", validators=[DataRequired()])
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
    email = None

    form = NamerForm()
    # Validate Data form Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form was submitted")
    return render_template('name.html',
                           name=name,
                           form=form)


@app.route('/test_pw', methods=['GET', 'POST'])
def password():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Data form Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Get user from data
        pw_to_check = Users.query.filter_by(email=email).first()
        # Compare hashed password with password in form
        passed = check_password_hash(pw_to_check.password_hash, password)
        form.email.data = ""
        form.password.data = ""
    return render_template('test_pw.html',
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    # Validate Data from Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_password = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favourite_color=form.favourite_color.data,
                         password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        form.favourite_color.data = ""
        form.password_hash.data = ""
        flash("User was added successfully")
    all_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html',
                           name=name,
                           form=form,
                           all_users=all_users)


# Update User in Database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.favourite_color = request.form['favourite_color']
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html', form=form, user=user)
        except:
            flash("Error! Try again")
            return render_template('update.html', form=form, user=user)
    else:
        return render_template('update.html', form=form, user=user)


@app.route('/delete/<int:id>')
def delete(id):
    user = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user)
        db.session.commit()
        all_users = Users.query.order_by(Users.date_added)
        flash("User deleted successfully")
        return render_template('add_user.html',
                               name=name,
                               form=form,
                               all_users=all_users)
    except:
        flash("We have some problems!!! Try again.")
        return render_template('add_user.html',
                               name=name,
                               form=form,
                               all_users=all_users)
