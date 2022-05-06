from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from forms import PostForm, UserForm, LoginForm, NamerForm, PasswordForm, SearchForm
from werkzeug.utils import secure_filename
from uuid import uuid1
import os
# Create a Flask Instance
app = Flask(__name__)
# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite"
# Secret Key
app.config['SECRET_KEY'] = 'This is my secret key'
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# Pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# Admin Page
@app.route('/admin')
@login_required
def admin():
    if current_user.id == 1:
        return render_template('admin.html')
    else:
        flash('Sorry, You are not admin')
        return redirect(url_for('dashboard'))


# Search function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=post.searched, posts=posts)


# All posts
@app.route('/posts')
def posts():
    posts = Posts.query.order_by('date_added')
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('single-post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    post = Posts.query.get_or_404(id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.poster.id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("update_post.html", post=post, form=form)
    else:
        flash("You aren't authorized to edit this post ")
        posts = Posts.query.order_by('date_added')
        return render_template('posts.html', posts=posts)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post = Posts.query.get_or_404(id)
    if current_user.id == post.poster.id:
        try:
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted successfully")
            posts = Posts.query.order_by('date_added')
            return render_template('posts.html', posts=posts)
        except:
            flash("Whoops something wrong happened")
            posts = Posts.query.order_by('date_added')
            return render_template('posts.html', posts=posts)
    else:
        flash("Sorry, you can't delete this post!!!")
        posts = Posts.query.order_by('date_added')
        return render_template('posts.html', posts=posts)


# Add Post
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        # Submit Form
        poster = current_user.id
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     poster_id=poster,
                     slug=form.slug.data)
        # Clear Form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        # Add post to database
        db.session.add(post)
        db.session.commit()
        flash('Post was successfully added')
        return redirect(url_for('posts'))
    return render_template('add_post.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('dashboard'))
            else:
                flash('Something wrong - Try again!')
        else:
            flash("That user doesn't exist!")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out!!!')
    return redirect(url_for('login'))


#
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


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
                         username=form.username.data,
                         email=form.email.data,
                         favourite_color=form.favourite_color.data,
                         about=form.about.data,
                         password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
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
@login_required
def update(id):
    form = UserForm()
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.username = request.form['username']
        user.email = request.form['email']
        user.favourite_color = request.form['favourite_color']
        user.about = request.form['about']
        user.profile_picture = request.files['profile_picture']
        # Grab image name to save in DB
        picture_filename = secure_filename(user.profile_picture.filename)
        # Set UUID
        picture_name = str(uuid1()) + '_' + picture_filename
        # Save that image
        user.profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_name))
        # Change it to a string to save in DB
        user.profile_picture = picture_name

        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html', form=form, user=user, id=id)
        except:
            flash("Error! Try again")
            return render_template('update.html', form=form, user=user, id=id)
    else:
        return render_template('update.html', form=form, user=user, id=id)


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


# Posts Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # author = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    favourite_color = db.Column(db.String(200))
    about = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    profile_picture = db.Column(db.String(), nullable=True)
    password_hash = db.Column(db.String(200))
    posts = db.relationship('Posts', backref='poster')

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
