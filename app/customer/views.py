from flask import render_template, redirect, request, url_for, flash,session
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import customer
from .. import db
from .forms import PurchaseFlightForm,ConfirmPurchaseForm
from ..models import Customer,BookingAgent,Airline_Staff,Airline,load_user,Flight, Ticket,Purchase,Airplane

from datetime import datetime,date

@customer.route('/myflights',methods=['GET','POST'])
def myflights():
    if not current_user.is_authenticated or not current_user.get_type()=='customer':
        return redirect(url_for('main.index'))
    data=db.session.query(Ticket,Purchase,Flight).join(Purchase,\
        Ticket.ticket_id==Purchase.ticket_id).join(Flight, Ticket.airline_name==Flight.airline_name)\
        .filter(Purchase.email_customer==current_user.get_identifier()).filter(Flight.departure_time >= datetime.now()).filter(Ticket.flight_num==Flight.flight_num).\
        filter(Ticket.departure_time==Flight.departure_time)
    return render_template('customer/customer_flights.html',data=data)

#TODO
@customer.route('/browse_flights',methods=['GET','POST'])
def browse_flights():
    pass

@customer.route('/purchase_flight',methods=['GET','POST'])
def purchase_flight():
    form=PurchaseFlightForm()
    if form.validate_on_submit():
        flight=db.session.query(Flight).filter_by(airline_name=form.airline_name.data,
                                                flight_num=form.flight_num.data,
                                                departure_time=form.departure.data,
                                      ).first()
        if flight is not None:
            ticket = db.session.query(Flight, Ticket).join(Ticket, Flight.airline_name == Ticket.airline_name & \
                                                           Flight.flight_num == Ticket.flight_num & \
                                                           Flight.departure_time == Ticket.departure_time).all()
            num_tickets = len(ticket)
            airplane = db.session.query(Airplane).filter_by(airline_name=flight.airline_name,
                                                            id=flight.airplane_id).first()
            capacity = airplane.seat_count
            if num_tickets == capacity:
                flash('This flight is fully booked ')
                return render_template('customer/book_flights.html', form=form)
            price = flight.price
            if num_tickets >= .7 * capacity:
                price *= 1.2

            session['price']=price
            session['airline']=form.airline_name.data
            session['flight_num']=form.flight_num.data
            session['departure']=form.departure.data
            print(session.get('price'))
            return redirect('confirm_purchase')
        flash(u'we need a real flight dawg')
    return render_template('customer/book_flights.html',form=form)

@customer.route('/confirm_purchase',methods=['GET','POST'])
def confirm_purchase():
    if ('airline' not in session) or ('flight_num' not in session) or ('departure' not in session):
        flash('no flight selected')
        return redirect(url_for('main.index'))
    print('price:',session.get('price'))
    airline_name=session.get('airline')
    flight_num = session.get('flight_num')
    departure_time = session.get('departure')
    price=session.get('price')

    session.pop('airline')
    session.pop('flight_num')
    session.pop('departure')
    session.pop('price')

    form=ConfirmPurchaseForm()

    if form.validate_on_submit():
        #Create ticket and Purchase objects
        ticket=Ticket(ticket_id=len(Ticket.query.all()),
                      airline_name=airline_name,
                      flight_num=flight_num,
                      departure_time=departure_time,
                      price=price)
        purchase=Purchase(ticket_id=ticket.ticket_id,
                          email_customer=current_user.get_id().split('_')[1:],
                          card_num=form.card_number.data,
                          card_expiration=form.card_expiration.data,
                          date=datetime.now())
        db.session.add(ticket)
        db.session.add(purchase)
        db.session.commit()
        flash('Purchase successful :)')

        session['airline'] = airline_name
        session['flight_num'] = flight_num
        session['departure'] = departure_time
        session['price'] = price
        return redirect(url_for('main.index'))
    flight = db.session.query(Flight).filter_by(airline_name=airline_name,
                                                flight_num=flight_num,
                                                departure_time=departure_time,
                                                ).first()

    arrival_time=flight.arrival_time
    source=flight.departs
    destination=flight.arrives

    session['airline'] = airline_name
    session['flight_num'] = flight_num
    session['departure'] = departure_time
    session['price']=price

    return render_template('customer/purchase_confirmation.html',form=form,
                           airline_name=airline_name,
                           flight_num=flight_num,
                           departure_time=departure_time,
                           arrival_time=arrival_time,
                           source=source,
                           destination=destination,
                            price=price)




    #2020-05-05 14:56:00


#TODO
@customer.route('/ratings',methods=['GET','POST'])
def ratings():
    pass

#TODO
@customer.route('/spending',methods=['GET','POST'])
def spending():
    pass
