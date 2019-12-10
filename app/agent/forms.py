from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField,IntegerField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import DateTimeLocalField
from wtforms import ValidationError
from ..models import Customer
from datetime import datetime,timedelta

class ConfirmPurchaseForm(FlaskForm):
    card_number = StringField('Credit/Debit Card Number')
    card_expiration = DateField('Card Expiration Date',format="%m/%d/%Y",validators=[DataRequired('mm/dd/YYYY')])
    card_name = StringField('Card Holder Name')
    confirmation_code = StringField('Confirmation Code', validators=[Length(3, 3)])
    submit = SubmitField('Confirm Purchase')

class PurchaseFlightForm(FlaskForm):
    airline_name=StringField('Airline name', validators=[DataRequired('Please enter an airline name'), Length(1, 64)])
    flight_num = IntegerField('Flight number', validators=[DataRequired('Please enter a flight number')])
    departure=DateTimeLocalField('Departure Date and Time',validators=[DataRequired('please enter a departure')],format='%Y-%m-%dT%H:%M')
    customer_email=StringField('Customer Email',validators=[DataRequired('please enter a customer')])
    submit = SubmitField('Find')


class CommissionForm(FlaskForm):
    start=DateField(
        "Start", format="%Y-%m-%d",
        default=datetime.today()+timedelta(days=-30),  ## Now it will call it everytime.
        validators=[DataRequired()]
    )
    end=DateField(
        "End", format="%Y-%m-%d",
        default=datetime.today,  ## Now it will call it everytime.
        validators=[DataRequired()]
    )
    submit = SubmitField('Confirm')
