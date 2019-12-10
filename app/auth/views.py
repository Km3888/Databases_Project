from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import Customer,BookingAgent,Airline_Staff,Airline,load_user
from .forms import StaffLoginForm,CustomerLoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm,UserTypeForm,\
    BookingAgentLoginForm,CustomerRegistrationForm,BookingAgentRegistrationForm,\
    StaffRegistrationForm



@auth.route('/login',methods=['GET','POST'])
def login():
    form=UserTypeForm()
    if form.validate_on_submit():
        return redirect('/auth/login/'+form.type.data)
    return render_template('auth/login.html',form=form)

@auth.route('/login/cust',methods=['GET','POST'])
def cust():
    form=CustomerLoginForm()
    if form.validate_on_submit():
        custy= Customer.query.filter_by(email=form.email.data.lower()).first()
        if custy is not None and custy.verify_password(form.password.data):
            login_user(custy,form.remember_me.data)
            next=request.args.get('next')
            if next is None or not next.startwith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html',form=form)

@auth.route('/login/agent', methods=['GET', 'POST'])
def agent():
    form=BookingAgentLoginForm()
    if form.validate_on_submit():
        agent=BookingAgent.query.filter_by(email=form.email.data.lower()).first()
        if agent is not None and agent.verify_password(form.password.data) and agent.verify_id(form.booking_agent_id.data):
            login_user(agent, form.remember_me.data)
            next=request.args.get('next')
            if next is None or not next.startwith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid username, password, or ID')
    return render_template('auth/login.html',form=form)


@auth.route('/login/staff',methods=['GET','POST'])
def staff():
    form = StaffLoginForm()
    if form.validate_on_submit():
        staff = Airline_Staff.query.filter_by(username=form.username.data.lower()).first()
        if staff is not None and staff.verify_password(form.password.data):
            login_user(staff, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startwith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=['GET','POST'])
def register():
    form=UserTypeForm()
    if form.validate_on_submit():
        return redirect('/auth/register/'+form.type.data)
    return render_template('auth/register.html',form=form)

@auth.route('/register/cust',methods=['GET','POST'])
def register_cust():
    form=CustomerRegistrationForm()
    if form.validate_on_submit():
        result=Customer.query.filter_by(email=form.email.data).first()
        if result is None:
            custy=Customer(email=form.email.data,
                           name=form.username.data,
                           password=form.password.data,
                           building_number=form.building_number.data,
                           street=form.street.data,
                           city=form.city.data,
                           state=form.state.data,
                           phone_num=form.phone_num.data,
                           passport_num=form.passport_num.data,
                           passport_expiration=form.passport_expiration.data,
                           passport_country=form.passport_country.data,
                           DOB=form.dob.data)
            db.session.add(custy)
            db.session.commit()
            flash('your account has been created')
            return redirect(url_for('auth.login'))
        flash('That email already has an account')
    return render_template('auth/register.html',form=form)

@auth.route('/register/agent',methods=['GET','POST'])
def register_agent():
    form=BookingAgentRegistrationForm()
    if form.validate_on_submit():
        result=BookingAgent.query.filter_by(email=form.email.data).first()
        if result is None:
            #TODO figure out why this is being weird
            new_agent=BookingAgent(email=form.email.data.lower(),
                                   booking_agent_id=form.id.data,
                                   password=form.password.data,)
            db.session.add(new_agent)
            db.session.commit()
            flash('you have successfully registered')
            return redirect(url_for('main.index'))
        flash('That username is taken')
    return render_template('auth/register.html',form=form)


@auth.route('/register/staff',methods=['GET','POST'])
def register_staff():
    form=StaffRegistrationForm()
    if form.validate_on_submit():
        result=Airline_Staff.query.filter_by(username=form.username.data).first()
        if result is None:
            airline_result = Airline.query.filter_by(name=form.airline_name.data).first()
            if airline_result is not None:
                #TODO more weirdness
                new_staff=Airline_Staff(username=form.username.data,
                                        password=form.password.data,
                                        first_name=form.first_name.data,
                                        last_name=form.last_name.data,
                                        date_of_birth=form.dob.data,
                                        airline_name=form.airline_name.data)
                db.session.add(new_staff)
                db.session.commit()
                flash('you have successfully registered')
                return redirect(url_for('main.index'))
            flash('You must enter a valid airline')
        flash('That username is taken')
    return render_template('auth/register.html',form=form)

# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated  \
#             and request.endpoint \
#             and request.blueprint != 'auth' \
#             and request.endpoint != 'static':
#         return redirect(url_for('auth.unconfirmed'))

# @auth.route('/unconfirmed')
# def unconfirmed():
#     if current_user.is_anonymous:
#         return redirect(url_for('main.index'))
#     return render_template('auth/unconfirmed.html')









