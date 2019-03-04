from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectMultipleField, widgets
from wtforms_alchemy import ModelForm, ModelFieldList, QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields import FormField
from models import storage, state, city, amenity
from flask import flash
from flask_login import current_user



class RegistrationForm(FlaskForm):
    first_name = StringField('first_name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('last_name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_email(self, email):
        all_users = storage.all('User').values()
        for user in all_users:
            if user.email == email.data:
                raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ReviewForm(FlaskForm):
    text = StringField('text',
                           validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Submit')



class UpdateAccountForm(FlaskForm):
    first_name = StringField('first_name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('last_name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')
    def validate_email(self, email):
        all_users = storage.all('User').values()
        for user in all_users:
            if user.email == email.data and user.email != current_user.email:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=20)])
    description = StringField('description', validators=[DataRequired(), Length(min=10)])
    number_rooms = IntegerField('number_rooms', validators=[DataRequired()])
    number_bathrooms = IntegerField('number_bathrooms', validators=[DataRequired()])
    max_guest = IntegerField('max_guest', validators=[DataRequired()])
    price_by_night = IntegerField('price_by_night', validators=[DataRequired()])
    all_ame = storage.all('Amenity').values()
    amenities = SelectMultipleField('Amenities',
                                    choices = [(ame.id, ame.name) for ame in all_ame],
                                    widget=widgets.ListWidget(prefix_label=True),
                                    option_widget=widgets.CheckboxInput())
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        all_users = storage.all('User').values()
        if email.data not in [user.email for user in all_users]:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
