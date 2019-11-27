from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import customer
from .. import db
from .forms import PurchaseFlightForm
from ..models import Customer,BookingAgent,Airline_Staff,Airline,load_user,Flight, Ticket,Purchase
# from .forms import StaffLoginForm,CustomerLoginForm, RegistrationForm, ChangePasswordForm,\
#     PasswordResetRequestForm, PasswordResetForm,UserTypeForm,\
#     BookingAgentLoginForm,CustomerRegistrationForm,BookingAgentRegistrationForm,\
#     StaffRegistrationForm

from datetime import datetime

@customer.route('/myflights',methods=['GET','POST'])
def myflights():
    if not current_user.is_authenticated or not current_user.get_type()=='customer':
        return redirect(url_for('main.index'))
    data=Ticket.query.join(Purchase).filter_by(email_customer=current_user.get_id())
    return render_template('customer/customer_flights.html',data=data)

#TODO
@customer.route('/browse_flights',methods=['GET','POST'])
def browse_flights():
    pass

@customer.route('purchase_flight',methods=['GET','POST'])
def purchase_flight():
    form=PurchaseFlightForm()
    if form.validate_on_submit():
        flight=Flight.query.filter_by(airline_name=form.airline_name.data,departure_time=form.departure.data,).first()
        if flight is None:
            flash(u'we need a real flight dawg')
        #calculate price
        return url_for('confirm_purchase')
    return render_template('customer/book_flights.html',form=form)

@customer.route('confirm_purchase',methods=['GET','POST'])
def confirm_purchase():
    pass

#TODO
@customer.route('/ratings',methods=['GET','POST'])
def ratings():
    pass

#TODO
@customer.route('/spending',methods=['GET','POST'])
def spending():
    pass
