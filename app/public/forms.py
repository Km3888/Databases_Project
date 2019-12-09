from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField,IntegerField
from wtforms.fields.html5 import DateTimeLocalField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Flight

class TwoWayForm(FlaskForm):
    source_city=StringField('Source City')
    dest_city=StringField('Destination City')
    source_airport = StringField('Source Airport')
    dest_airport = StringField('Destination Airport')
    dest_date = DateField('Destination Date',validators=[DataRequired(message='Mandatory')])
    return_date = DateField('Return Date',validators=[DataRequired(message='Mandatory')])
    submit = SubmitField('Search')

class OneWayForm(FlaskForm):
    source_city=StringField('Source City')
    dest_city=StringField('Destination City')
    source_airport = StringField('Source Airport')
    dest_airport = StringField('Destination Airport')
    flight_date = DateField('Flight Date',validators=[DataRequired(message='dd/mm/yyyy')])
    submit = SubmitField('Search')

class FlightTypeForm(FlaskForm):
    type = SelectField(u'Trip type', choices=[('one', 'One Way'), ('two', 'Round Trip')])
    submit = SubmitField('Continue')


# for queries in views - not sure if set error in forms or views

# make source_city, dest_city, and dest_date required
# add conditions that dest_date after today
# add conditions that return_date after arrival date of 1st flight
# or for now just that return_date 24hr after dest_date
# set errors for:
# source city and airport don't match
# dest city and dest don't match
# source and dest city same
# source and dest airport same

# do we add field for searching for one-way or round-trip?



class SeeFlightsStatus(FlaskForm):
    airline_name=StringField('Airline Name', validators=[DataRequired(), Length(1, 64)])
    flight_num = IntegerField('Flight Number', validators=[DataRequired()])
    departure_time = DateTimeLocalField('Departure Time', validators=[DataRequired()],format='%Y-%m-%dT%H:%M')
    submit=SubmitField('Search')
