from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.fields.html5 import DateField
from methods import get_categories
from wtforms.validators import Optional, InputRequired, Email


class AdvancedSearchForm(FlaskForm):
    """form for advanced searches"""

    keyword = StringField("Keyword", default="")
    location = StringField("Location", default="")
    category=SelectField("Category", choices=get_categories())
    start_date=DateField("From", validators=[Optional()])
    end_date=DateField("To", validators=[Optional()])

class LogInForm(FlaskForm):
    """form for logging in a user"""
    email = StringField("Email", validators=[Email(), InputRequired()])
    password=PasswordField("Password", validators=[InputRequired()])

class SignUpForm(FlaskForm):
    """form for signing up a user"""
    email = StringField("Email", validators=[Email(), InputRequired()])
    password=PasswordField("Password", validators=[InputRequired()])
    first_name=StringField("First Name", validators=[InputRequired()])
    last_name=StringField("Last Name", validators=[InputRequired()])
    location=StringField("Default Location", validators=[InputRequired()])

class NewPasswordForm(FlaskForm):
    """form to change password"""
    cur_password = PasswordField(
        'Current Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired()])
    conf_password = PasswordField(
        'Confirm New Password', validators=[InputRequired()])

class EditUserForm(FlaskForm):
    """update user form"""
    email = StringField('E-mail', validators=[Email()])
    first_name=StringField("First Name", validators=[InputRequired()])
    last_name=StringField("Last Name", validators=[InputRequired()])
    location=StringField("Default Location", validators=[InputRequired()])
    password = PasswordField('Password')

class FilterCategoryForm(FlaskForm):
     """a form to filter results by category"""
     category=SelectField("Category", choices=get_categories())