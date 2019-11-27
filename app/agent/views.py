from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import agent
from .. import db
from ..models import Customer,BookingAgent,Airline_Staff,Airline,Ticket,Purchase
# from .forms import StaffLoginForm,CustomerLoginForm, RegistrationForm, ChangePasswordForm,\
#     PasswordResetRequestForm, PasswordResetForm,UserTypeForm,\
#     BookingAgentLoginForm,CustomerRegistrationForm,BookingAgentRegistrationForm,\
#     StaffRegistrationForm
from sqlalchemy.sql import func


@agent.route('/stats',methods=['GET','POST'])
def stats():
    data=db.session.query(Purchase).all()
    
    # query=Purchase.query.filter_by(email_booking = current_user.get_identifier()).join(Ticket).all()
    return render_template('public/view_searchfutureflights.html',data=data)