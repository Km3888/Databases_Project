from flask.ext.wtf import Form
from wtfforms import StringField, PasswordField, BooleanField, SubmitField,ValidationError
from wtforms.validators import DataRequired,Length, Regexp, EqualTo
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in') submit = SubmitField('Log In')

class RegistrationForm(Form):

    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    booking_agent_id=StringField('Booking_agent_id',validators=[DataRequired(),Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'ID must have only letters, numbers, dots or underscores')])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Passwords must match')])
    password2=PasswordField('Confirm Password',validators=[DataRequired()])

    submit=SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError

