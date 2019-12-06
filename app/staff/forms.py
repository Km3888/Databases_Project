from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField,IntegerField
from wtforms.fields.html5 import DateTimeLocalField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Purchase, Ticket

class ReportForm(FlaskForm):
    start=DateField("Start", format="%Y-%m-%d",\
            validators=[DataRequired()])
    end=DateField("End", format="%Y-%m-%d",\
            validators=[DataRequired()])
    submit = SubmitField('Display Report')
