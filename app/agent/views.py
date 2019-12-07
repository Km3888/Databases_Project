from flask import render_template, redirect, request, url_for, flash,session
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import agent
from .. import db
from ..models import Customer,BookingAgent,Airline_Staff,Airline,Ticket,Purchase,Flight,Airplane
from .forms import ConfirmPurchaseForm,CommissionForm,PurchaseFlightForm
from datetime import datetime,timedelta
from sqlalchemy.sql import func
from sqlalchemy.sql import desc


@agent.route('/topcustomers',methods=['GET','POST'])
def topcustomers():

    date_six_months_ago=datetime.now()-timedelta(days=180)
    date_year_ago=datetime.now()-timedelta(days=365)
    top_num_tickets=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_customer, Purchase.email_booking, Ticket.ticket_id).with_entities(Purchase.email_customer, func.count(Ticket.ticket_id).label('count_tickets')).group_by(Purchase.email_customer).filter(Purchase.email_booking==current_user.get_identifier()).filter(Purchase.date>date_six_months_ago).order_by(desc("count_tickets"))[:5]

    # make list of customer names
    # make list of number of tickets puchased

    customers=[]
    num_tickets=[]

    for line in top_num_tickets:
        cust=line.email_customer
        tick=line.count_tickets
        customers.append(cust)
        num_tickets.append(tick)

    top_commissions=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id)\
                        .add_columns(Purchase.email_customer, Purchase.email_booking, Ticket.ticket_id, Ticket.price)\
                        .with_entities(Purchase.email_customer, (func.sum(Ticket.price)/10).label('sum_commissions'))\
                        .group_by(Purchase.email_customer).filter(Purchase.email_booking==current_user.get_identifier())\
                        .filter(Purchase.date>date_year_ago).order_by(desc("sum_commissions"))[:5]

    com_customers=[]
    list_commissions=[]

    for line in top_commissions:
        cust=line.email_customer
        com=line.sum_commissions
        com_customers.append(cust)
        list_commissions.append(com)

    # query=Purchase.query.filter_by(email_booking = current_user.get_identifier()).join(Ticket).all()
    return render_template('agent/viewtopcustomers.html',top_num_tickets=top_num_tickets,\
                                                            customers=customers,\
                                                            num_tickets=num_tickets,\
                                                            top_commissions=top_commissions,\
                                                            com_customers=com_customers,\
                                                            list_commissions=list_commissions,\
                                                            max=max(num_tickets),\
                                                            max_comm=max(list_commissions))

@agent.route('/your_commission',methods=['GET','POST'])
def your_commission():
    form=CommissionForm()
    if form.validate_on_submit():
        start_date=form.start
        end_date=form.end
        earliest = datetime.combine(start_date.data, datetime.min.time())
        latest = datetime.combine(end_date.data + timedelta(days=1), datetime.min.time())
        data=db.session.query(Ticket,Purchase).join(Purchase,Ticket.ticket_id==Purchase.ticket_id)\
            .filter(Purchase.email_booking==current_user.get_identifier()).filter(Purchase.date>=earliest).filter(Purchase.date<=latest).all()
        total=0
        for row in data:
            total+=row[0].price
        total/=10
        return render_template('agent/display_commission.html',commission=total)
    return render_template('agent/commission_form.html',form=form)

#TODO check functioniality
@agent.route('/my_flights',methods=['GET','POST'])
def my_flights():
    if not current_user.is_authenticated or not current_user.get_type()=='agent':
        return redirect(url_for('main.index'))
    data=db.session.query(Ticket,Purchase,Flight).join(Purchase,\
        Ticket.ticket_id==Purchase.ticket_id).join(Flight, Ticket.airline_name==Flight.airline_name)\
        .filter(Purchase.email_booking==current_user.get_identifier()).filter(Flight.departure_time >= datetime.now()).filter(Ticket.flight_num==Flight.flight_num).\
        filter(Ticket.departure_time==Flight.departure_time)
    return render_template('customer/passenger_list.html',data=data)

@agent.route('/book_flight',methods=['GET','POST'])
def book_flight():
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
            customer=db.session.query(Customer).filter(Customer.email==form.customer_email).first()
            if customer is None:
                flash('This customer does not exist ')
                return render_template('customer/book_flights.html', form=form)
            price = flight.price
            if num_tickets >= .7 * capacity:
                price *= 1.2

            session['price']=price
            session['airline']=form.airline_name.data
            session['flight_num']=form.flight_num.data
            session['departure']=form.departure.data
            session['customer']=form.customer

            return redirect('confirm_purchase')
        flash(u'we need a real flight dawg')
    return render_template('customer/book_flights.html',form=form)


@agent.route('/confirm_purchase',methods=['GET','POST'])
def confirm_purchase():
    if ('airline' not in session) or ('flight_num' not in session) or ('departure' not in session):
        flash('no flight selected')
        return redirect(url_for('main.index'))
    session.pop('airline')
    session.pop('flight_num')
    session.pop('departure')
    session.pop('price')
    session.pop('customer')

    form=ConfirmPurchaseForm()
    airline_name = session.get('airline')
    flight_num = session.get('flight_num')
    departure_time = session.get('departure')
    price = session.get('price')
    customer = session.get('customer')


    if form.validate_on_submit():

        ticket = Ticket(ticket_id=len(Ticket.query.all()),
                        airline_name=airline_name,
                        flight_num=flight_num,
                        departure_time=departure_time,
                        price=price)
        purchase = Purchase(ticket_id=ticket.ticket_id,
                            email_customer=customer,
                            email_booking=current_user.get_identifier(),
                            card_num=form.card_number.data,
                            card_expiration=form.card_expiration.data,
                            date=datetime.now())
        db.session.add(ticket)
        db.session.add(purchase)
        db.session.commit()
        flash('Purchase successful :)')
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
    session['customer']=customer
    return render_template('agent/purchase_confirmation.html', form=form,
                           airline_name=airline_name,
                           flight_num=flight_num,
                           departure_time=departure_time,
                           arrival_time=arrival_time,
                           source=source,
                           destination=destination,
                           price=price)
