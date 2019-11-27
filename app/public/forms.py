from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Flight

class TwoWayForm(FlaskForm):
    source_city=StringField('Source City',validators=[DataRequired(message='Mandatory')])
    dest_city=StringField('Destination City',validators=[DataRequired(message='Mandatory')])
    source_airport = StringField('Source Airport')
    dest_airport = StringField('Destination Airport')
    dest_date = DateField('Destination Date',validators=[DataRequired(message='Mandatory')],format='%d/%m/%Y')
    return_date = DateField('Return Date',validators=[DataRequired(message='Mandatory')],format='%d/%m/%Y')
    submit = SubmitField('Search')

class OneWayForm(FlaskForm):
    source_city=StringField('Source City',validators=[DataRequired(message='Mandatory')])
    dest_city=StringField('Destination City',validators=[DataRequired(message='Mandatory')])
    source_airport = StringField('Source Airport')
    dest_airport = StringField('Destination Airport')
    flight_date = DateField('Flight Date',validators=[DataRequired(message='Mandatory')],format='%d/%m/%Y')
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
    flight=StringField('SampleSee', validators=[DataRequired(), Length(1, 64)])
    submit=SubmitField('Search')
