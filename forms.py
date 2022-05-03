from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea


class SearchForm(FlaskForm):
    searched = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    title = StringField("Enter title", validators=[DataRequired()])
    content = StringField("Enter content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Enter author")
    slug = StringField("Enter slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    username = StringField("Enter your username", validators=[DataRequired()])
    email = StringField("Enter your email", validators=[DataRequired()])
    favourite_color = StringField("Enter your favourite color", validators=[DataRequired()])
    password_hash = PasswordField("Enter your password", validators=[DataRequired(),
                                                                     EqualTo('password_hash2',
                                                                             message='Passwords Must Match')])
    password_hash2 = PasswordField("Submit your password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Enter your username", validators=[DataRequired()])
    password = PasswordField("Enter your username", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's your email?", validators=[DataRequired()])
    password = PasswordField("What's your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")
