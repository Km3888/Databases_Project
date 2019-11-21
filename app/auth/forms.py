from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import Customer

class UserTypeForm(FlaskForm):
    type=SelectField(u'Account type',choices=[('staff','Staff'),('cust','Customer'),('agent','Booking Agent')])
    submit=SubmitField('Continue')

class CustomerLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class BookingAgentLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    booking_agent_id=StringField('Booking Agent ID',validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class StaffLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class CustomerRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Mandatory'), Length(1, 64)])
    username = StringField('Username', validators=[
        DataRequired(message='Mandatory'), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired(message='Mandatory')])

    state=StringField('State',validators=[DataRequired(message='Mandatory'),Length(1,2)])
    city=StringField('City',validators=[DataRequired(message='Mandatory'),Length(1,64)])
    street=StringField('Street',validators=[DataRequired(message='Mandatory'),Length(1,64)])
    building_number = StringField('Building Number')

    phone_num = StringField('Phone Number', validators=[DataRequired(message='Mandatory'), Length(7, 16)])
    passport_num = StringField('Passport Number', validators=[DataRequired(message='Mandatory'), Length(9, 9)])
    passport_expiration = DateField('Passport Expiration Date', validators=[DataRequired(message="You must enter expiration date")], format='%d/%m/%Y')
    passport_country= StringField('Passport Country', validators=[DataRequired(message='Mandatory'), Length(1, 64)])

    dob=DateField('Date of Birth', validators=[DataRequired(message="You must enter date of birth")], format='%d/%m/%Y')

    submit = SubmitField('Register')

    def validate_username(self, field):
        if Customer.query.filter_by(email=field.data).first():
            raise ValidationError('Username already in use.')

class BookingAgentRegistrationForm(FlaskForm):
    email = StringField('Username', validators=[
        DataRequired(message='Mandatory'), Length(1, 64)])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired(message='Mandatory')])
    id=StringField('Agent id')
    submit=SubmitField('Register')


class StaffRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Mandatory'), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired(message='Mandatory')])
    first_name=StringField('First Name',validators=[DataRequired(message='Mandatory'),Length(1,64)])
    last_name= StringField('Last Name', validators=[DataRequired(message='Mandatory'), Length(1, 64)])
    dob = DateField('Date of Birth', validators=[DataRequired(message="You must enter date of birth")],
                    format='%d/%m/%Y')
    airline_name=StringField('Airline Name',validators=[DataRequired(message='Mandatory'),Length(1,64)])

    submit = SubmitField('Register')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

