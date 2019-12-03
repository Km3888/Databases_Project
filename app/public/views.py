from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import public
from .. import db
from ..models import Flight,Customer,BookingAgent,Airline_Staff,Airline,load_user,Airport, Airplane,Ticket
from .forms import SeeFlightsStatus,OneWayForm,TwoWayForm,FlightTypeForm
from sqlalchemy.orm import aliased
from datetime import datetime,timedelta

def compute_price(flight_num,airline_name,departure_time):
    # calculate price
    flight = db.session.query(Flight).filter_by(airline_name=airline_name,
                                                flight_num=flight_num,
                                                departure_time=departure_time).first()

    price = flight.price
    ticket = db.session.query(Flight, Ticket).join(Ticket, Flight.airline_name == Ticket.airline_name & \
                                                   Flight.flight_num == Ticket.flight_num & \
                                                   Flight.departure_time == Ticket.departure_time).all()
    num_tickets = len(ticket)
    airplane = db.session.query(Airplane).filter_by(airline_name=flight.airline_name, id=flight.airplane_id).first()
    capacity = airplane.seat_count
    if num_tickets >= .7 * capacity:
        price *= 1.2
    return price

@public.route('/searchfutureflights',methods=['GET','POST'])
def searchfutureflights():
    form= FlightTypeForm()
    if form.validate_on_submit():
        type=form.type.data
        if type=='one':
            return redirect('/public/oneway')
        else:
            return redirect('/public/twoway')
    return render_template('public/flight_search.html',form=form)

@public.route('/buy_or_book',methods=['GET','POST'])
def buy_or_book():
    if not current_user.is_authenticated or current_user.get_type()=='staff':
        flash('Must be logged in as customer or booking agent')
        return redirect('/main.index')
    if current_user.get_type()=='customer':
        return redirect('/customer/confirm_purchase')
    if current_user.get_type()=='agent':
        return redirect('agent.confirm_purchase')

@public.route('/twoway',methods=['GET','POST'])
def twoway():
    form = TwoWayForm()
    if form.validate_on_submit():
        first = aliased(Airport)
        second = aliased(Airport)
        earliest = datetime.combine(form.dest_date.data, datetime.min.time())
        latest = datetime.combine(form.dest_date.data + timedelta(days=1), datetime.min.time())
        data=db.session.query(Flight, first, second).join(first, Flight.departs == first.name) \
            .join(second, Flight.arrives == second.name). \
            filter(Flight.departure_time > earliest).filter(Flight.departure_time < latest)
        if len(form.source_city.data) > 0:
            data = data.filter(first.city == form.source_city.data)
        if len(form.dest_city.data) > 0:
            data = data.filter(second.city == form.dest_city.data)
        if len(form.source_airport.data) > 0:
            data = data.filter(first.name == form.source_airport.data)
        if len(form.dest_airport.data) > 0:
            data = data.filter(second.name == form.dest_airport.data)
        data1 = data.all()
        earliest = datetime.combine(form.return_date.data, datetime.min.time())
        latest = datetime.combine(form.return_date.data + timedelta(days=1), datetime.min.time())

        data=db.session.query(Flight, first, second).join(first, Flight.departs == first.name) \
            .join(second, Flight.arrives == second.name). \
            filter(Flight.departure_time > earliest).filter(Flight.departure_time < latest)

        if len(form.source_city.data) > 0:
            data = data.filter(second.city == form.source_city.data)
        if len(form.dest_city.data) > 0:
            data = data.filter(first.city == form.dest_city.data)
        if len(form.source_airport.data) > 0:
            data = data.filter(second.name == form.source_airport.data)
        if len(form.dest_airport.data) > 0:
            data = data.filter(first.name == form.dest_airport.data)
        data2=data.all()

        return render_template('public/two_way_flight_search.html', data1=data1,data2=data2, compute_price=compute_price)
    return render_template('public/searchfutureflights.html', form=form)



@public.route('/oneway',methods=['GET','POST'])
def oneway():
    form=OneWayForm()
    if form.validate_on_submit():
        first=aliased(Airport)
        second=aliased(Airport)
        earliest=datetime.combine(form.flight_date.data,datetime.min.time())
        latest=datetime.combine(form.flight_date.data+timedelta(days=1),datetime.min.time())


        data=db.session.query(Flight,first,second).join(first,Flight.departs==first.name) \
            .join(second, Flight.arrives == second.name). \
            filter(Flight.departure_time > earliest).filter(Flight.departure_time < latest)

        if len(form.source_city.data)>0:
            data=data.filter(first.city==form.source_city.data)
        if len(form.dest_city.data)>0:
            data=data.filter(second.city==form.dest_city.data)
        if len(form.source_airport.data)>0:
            data=data.filter(first.name==form.source_airport.data)
        if len(form.dest_airport.data)>0 :
            data=data.filter(second.name==form.dest_airport.data)
        data=data.all()
        return render_template('public/view_searchfutureflights.html',data=data,compute_price=compute_price)
    return render_template('public/searchfutureflights.html', form=form)


@public.route('/seeflightsstatus',methods=['GET','POST'])
def seeflightsstatus():
    form=SeeFlightsStatus()
    # if form.validate_on_submit():
        # where it goes once submitted
        # test to see which part bugginb
        # return redirect('main.index')
        #return redirect('/auth/searchfutureflights/'+form.type.data)
    # what happens if not submitted
    return render_template('public/seeflightsstatus.html',form=form)
