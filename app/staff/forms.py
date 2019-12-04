from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField,IntegerField
from wtforms.fields.html5 import DateTimeLocalField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Flight


class ChangeStatusForm(FlaskForm):
    flight_num=StringField('Flight number',validators=[DataRequired(message='Mandatory')])
    departure_time=DateTimeLocalField('Flight departure time',validators=[DataRequired(message='Mandatory')])
    new_status=StringField('New Status',validators=[DataRequired(message='Mandatory')])
    submit=SubmitField('Change Status')

class AddAirplaneForm(FlaskForm):
    airplane_id=IntegerField('Airplane ID number',validators=[DataRequired(message='Mandatory')])
    seat_count=IntegerField('Number of Seats in New Airplane',validators=[DataRequired(message='Mandatory')])
    submit=SubmitField('Add Flight')

class AddFlightForm(FlaskForm):
    flight_num=IntegerField('Flight Number',validators=[DataRequired(message='Mandatory')])
    departure_time=DateTimeLocalField('Flight Departure Time',validators=[DataRequired(message='Mandatory')])
    arrival_time = DateTimeLocalField('Flight Arrival Time', validators=[DataRequired(message='Mandatory')])
    price=IntegerField('Flight Price',validators=[DataRequired(message='Mandatory')])
    status=StringField('Flight Status',validators=[DataRequired(message='Mandatory')])
    departs=StringField('Departure Airport',validators=[DataRequired(message='Mandatory')])
    arrives=StringField('Arrival Airport',validators=[DataRequired(message='Mandatory')])
    airplane_id=IntegerField('Airplane id',validators=[DataRequired(message='Mandatory')])
    submit=SubmitField('Add Flight')