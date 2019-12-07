from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField,IntegerField
from wtforms.fields.html5 import DateTimeLocalField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Customer



class PurchaseFlightForm(FlaskForm):
    airline_name=StringField('Airline name', validators=[DataRequired('Please enter an airline name'), Length(1, 64)])
    flight_num = IntegerField('Flight number', validators=[DataRequired('Please enter a flight number')])
    departure=DateTimeLocalField('Departure Date and Time',validators=[DataRequired('please enter a departure')],format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Find')

class ConfirmPurchaseForm(FlaskForm):
    card_number=StringField('Credit/Debit Card Number')
    card_expiration=DateField('Card Expiration Date')
    card_name=StringField('Card Holder Name')
    confirmation_code=StringField('Confirmation Code',validators=[Length(3,3)])
    submit = SubmitField('Confirm Purchase')

class CompletedFlights(FlaskForm):
    airline_name=StringField('Airline name', validators=[DataRequired('Please enter an airline name'), Length(1, 64)])
    flight_num = IntegerField('Flight number', validators=[DataRequired('Please enter a flight number')])
    departure=DateTimeLocalField('Departure Date and Time',validators=[DataRequired('Please enter a departure')],format='%Y-%m-%dT%H:%M')
    rating=IntegerField('Rate out of 5')
    comment=StringField('Comment')
    submit = SubmitField('Submit')

class SpendingForm(FlaskForm):
    start=DateField("Start", format="%Y-%m-%d",\
            validators=[DataRequired()])
    end=DateField("End", format="%Y-%m-%d",\
            validators=[DataRequired()]),
    submit = SubmitField('Display Spending')
