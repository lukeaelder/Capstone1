from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SignupForm(FlaskForm):
    """From for creating a user."""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[Length(min=6)])

class ReviewForm(FlaskForm):
    """Form for creating a review."""

    title = StringField('Title', validators=[DataRequired(), Length(max=30)])
    body = TextAreaField('Review', validators=[DataRequired(), Length(max=200)])
    rating = IntegerField('Rating (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])

class UserEditForm(FlaskForm):
    """Form for editing a user."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Profile Image URL')
    bio = TextAreaField('(Optional) Bio', validators=[Length(max=150)])

class CreateList(FlaskForm):
    """Form for creating a list."""

    title = StringField('Title', validators=[DataRequired(), Length(max=30)])
    description = TextAreaField('(Optional) Description', validators=[Length(max=200)])
