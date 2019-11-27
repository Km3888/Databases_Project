from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField,IntegerField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Customer



class PurchaseFlightForm(FlaskForm):
    airline_name=StringField('Airline name', validators=[DataRequired('Please enter an airline name'), Length(1, 64)])
    flight_num = IntegerField('Flight number', validators=[DataRequired('Please enter a flight number')])
    departure=DateTimeLocalField('Departure Date and Time',validators=[DataRequired('please enter a departure')],format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Find')