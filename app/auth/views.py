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

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data.lower()).first()
#         if user is not None and user.verify_password(form.password.data):
#             login_user(user, form.remember_me.data)
#             next = request.args.get('next')
#             if next is None or not next.startswith('/'):
#                 next = url_for('main.index')
#             return redirect(next)
#         flash('Invalid email or password.')
#     return render_template('auth/login.html', form=form)

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

# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(email=form.email.data.lower(),
#                     username=form.username.data,
#                     password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         token = user.generate_confirmation_token()
#         send_email(user.email, 'Confirm Your Account',
#                    'auth/email/confirm', user=user, token=token)
#         flash('A confirmation email has been sent to you by email.')
#         return redirect(url_for('auth.login'))
#     return render_template('auth/register.html', form=form)


# @auth.route('/confirm/<token>')
# @login_required
# def confirm(token):
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#     if current_user.confirm(token):
#         db.session.commit()
#         flash('You have confirmed your account. Thanks!')
#     else:
#         flash('The confirmation link is invalid or has expired.')
#     return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

#TODO
# @auth.route('/reset', methods=['GET', 'POST'])
# def password_reset_request():
#     if not current_user.is_anonymous:
#         return redirect(url_for('main.index'))
#     form = PasswordResetRequestForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data.lower()).first()
#         if user:
#             token = user.generate_reset_token()
#             send_email(user.email, 'Reset Your Password',
#                        'auth/email/reset_password',
#                        user=user, token=token)
#         flash('An email with instructions to reset your password has been '
#               'sent to you.')
#         return redirect(url_for('auth.login'))
#     return render_template('auth/reset_password.html', form=form)


#TODO
# @auth.route('/reset/<token>', methods=['GET', 'POST'])
# def password_reset(token):
#     if not current_user.is_anonymous:
#         return redirect(url_for('main.index'))
#     form = PasswordResetForm()
#     if form.validate_on_submit():
#         if User.reset_password(token, form.password.data):
#             db.session.commit()
#             flash('Your password has been updated.')
#             return redirect(url_for('auth.login'))
#         else:
#             return redirect(url_for('main.index'))
#     return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
