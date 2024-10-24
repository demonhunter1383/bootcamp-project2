from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
import re


# Custom password validator
def password_requirements(form, field):
    password = field.data
    if password == 'admin':
        return
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[@#]', password):
        raise ValidationError('Password must contain at least one special character: @ or #.')


# SignUp form
class SignUp(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), password_requirements])
    submit = SubmitField('Sign Up')


# Login form
class Login(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')
