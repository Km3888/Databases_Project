from flask import render_template, redirect, request, url_for, flash,session
from flask_login import current_user
from . import staff
from .. import db
from ..models import Purchase,Ticket,Customer,BookingAgent,Airline_Staff,Airline,load_user,Flight,Airplane,Airport
from datetime import datetime,date, timedelta
from .forms import ChangeStatusForm,AddAirplaneForm,AddFlightForm,AddAirportForm,FrequentCustomersForm,AirlineFlightsForm,PassengerListForm
from sqlalchemy import func
from sqlalchemy.orm import aliased

#TODO - question for prof
    # top 5 based on num of tickets - past month (last 30 days)
    # top 5 based on num of tickets - past year (last 365 days)
    # top 5 based on commission - last month (last 30 days)

#TODO check change_flight_status
@staff.route('/change_flight_status',methods=['GET','POST'])
def change_flight_status():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    form=ChangeStatusForm()
    if form.validate_on_submit():
        airline_name=db.session.query(Airline_Staff).filter(Airline_Staff.username==current_user.get_identifier()).first().airline_name
        flight_num=form.flight_num.data
        departure_time=form.departure_time.data
        flight=db.session.query(Flight).filter_by(airline_name=airline_name,flight_num=flight_num,departure_time=departure_time).first()
        if flight is not None:
            flight.status=form.new_status.data
            db.session.commit()
            flash('Updated status to:'+form.new_status.data)
            return redirect(url_for('main.index'))
        flash('Could not find this flight for your airline')
    return render_template('staff/change_flight_status.html',form=form)

#TODO check add_airplane
@staff.route('/add_airplane',methods=['GET','POST'])
def add_airplane():
    #TODO add_airplane form
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    form=AddAirplaneForm()
    if form.validate_on_submit():
        airline_name = db.session.query(Airline_Staff).filter(Airline_Staff.username == current_user.get_identifier()).first().airline_name
        plane_id=form.airplane_id.data
        seat_count=form.seat_count.data
        plane=db.session.query(Airplane).filter_by(airline_name=airline_name,plane_id=plane_id).first()
        if plane is None:
            new_plane=Airplane(airline_name=airline_name,plane_id=plane_id,seat_count=seat_count)
            db.session.add(new_plane)
            db.session.commit()
        flash('There is already a flight with this ID in your airline')
    return render_template('staff/add_airplane.html',form=form)

#TODO check add_flight
@staff.route('/add_flight',methods=['GET','POST'])
def add_flight():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    form=AddFlightForm()
    if form.validate_on_submit():
        airline_name = db.session.query(Airline_Staff).filter(Airline_Staff.username == current_user.get_identifier()).first().airline_name
        flight_num=form.flight_num.data
        departure_time=form.departure_time.data
        arrival_time=form.arrival_time.data
        price=form.price.data
        status=form.status.data
        departs=form.departs.data
        arrives=form.arrives.data
        airplane_id=form.airplane_id.data

        flight=db.session.query(Flight).filter_by(airline_name=airline_name,flight_num=flight_num,departure_time=departure_time).first()
        if flight is not None:
            flash('There is already a flight with that number and departure time in your airline')
            return render_template('staff/add_airplane.html',form=form)
        airplane=db.session.query(Airplane).filter_by(airline_name=airline_name,id=airplane_id).first()
        if airplane is None:
            flash('There is no airplane with this id in your airline')
            return render_template('staff/add_airplane.html',form=form)
        departs_airport=db.session.query(Airport).filter_by(name=departs).first()
        if departs_airport is None:
            flash('There is no airport with this name(departure airport)')
            return render_template('staff/add_airplane.html',form=form)
        arrives_airport = db.session.query(Airport).filter_by(name=arrives).first()
        if arrives_airport is None:
            flash('There is no airport with this name(departure airport)')
            return render_template('staff/add_airplane.html',form=form)
        new_flight=Flight(airline_name=airline_name,
                          flight_num=flight_num,
                          departure_time=departure_time,
                          arrival_time=arrival_time,
                          price=price,
                          status=status,
                          departs=departs,
                          arrives=arrives,
                          airplane_id=airplane_id)
        db.session.add(new_flight)
        db.session.commit()
        flash('Added Flight')
        return redirect(url_for('main.index'))

    return render_template('staff/add_airplane.html',form=form)

#TODO check add_airport
@staff.route('/add_airport',methods=['GET','POST'])
def add_airport():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    form=AddAirportForm()
    if form.validate_on_submit():
        name=form.name.data
        city=form.city.data
        airport=db.session.query(Airport).filter_by(name=name).first()
        if airport is None:
            new_airport=Airport(name=name,city=city)
            db.session.add(new_airport)
            db.session.commit()
            flash('Added airport')
            return redirect(url_for('main.index'))
        flash('There is already an airport with that name')
    return render_template('staff/add_airport.html',form=form)

@staff.route('/frequent_customers',methods=['GET','POST'])
def frequent_customers():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    airline_name = db.session.query(Airline_Staff).filter(
        Airline_Staff.username == current_user.get_identifier()).first().airline_name
    freq_customer=db.session.query(Purchase.email_customer,func.count(Purchase.ticket_id)).join(Ticket,Purchase.ticket_id==Ticket.ticket_id)\
        .filter(Ticket.airline_name==airline_name).group_by(Purchase.email_customer).order_by(func.count(Purchase.ticket_id).desc()).first()[0]
    if freq_customer is None:
        flash('Looks like no-one has bought anything from your airline yet')
    form=FrequentCustomersForm()
    if form.validate_on_submit():
        customer=db.session.query(Customer).filter_by(email=form.email.data).first()
        if customer is not None:
            session['email']=form.email.data
            return redirect('view_customer_flights')
        flash('This user does not exist')
    return render_template('staff/frequent_customers.html',form=form,freq_customer=freq_customer)

@staff.route('/view_customer_flights',methods=['GET','POST'])
def view_customer_flights():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    email=session.get('email')
    session.pop('email')
    airline_name = db.session.query(Airline_Staff).filter(
        Airline_Staff.username == current_user.get_identifier()).first().airline_name

    data=db.session.query(Purchase,Ticket,Flight).join(Ticket,Ticket.ticket_id==Purchase.ticket_id).\
        join(Flight,Flight.airline_name==Ticket.airline_name).filter(Flight.flight_num==Ticket.flight_num).\
        filter(Flight.departure_time==Ticket.departure_time).\
        filter(Ticket.airline_name==airline_name).order_by(Ticket.departure_time).filter(Purchase.email_customer==email)
    data=data.all()
    session['email']=email
    return render_template('staff/view_customer_flights.html',data=data,email=email)

@staff.route('/top_destinations',methods=['GET','POST'])
def top_destinations():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    airline_name = db.session.query(Airline_Staff).filter(
        Airline_Staff.username == current_user.get_identifier()).first().airline_name

    last_90=datetime.now()-timedelta(days=90)
    last_365=datetime.now()-timedelta(days=365)
    top_90=db.session.query(Flight.arrives,func.count(Ticket.ticket_id)).\
        join(Flight,Flight.airline_name==Ticket.airline_name).filter\
        (Flight.departure_time==Ticket.departure_time).filter\
        (Flight.flight_num==Ticket.flight_num).filter(Flight.airline_name==airline_name).\
        filter(Flight.departure_time>=last_90).group_by(Flight.arrives).\
        order_by(func.count(Ticket.ticket_id)).all()[:5]
    top_365 = db.session.query(Flight.arrives, func.count(Ticket.ticket_id)). \
        join(Flight, Flight.airline_name == Ticket.airline_name).filter \
        (Flight.departure_time == Ticket.departure_time).filter \
        (Flight.flight_num == Ticket.flight_num).filter(Flight.airline_name == airline_name). \
        filter(Flight.departure_time >= last_365).group_by(Flight.arrives).\
                  order_by(func.count(Ticket.ticket_id)).all()[:5]
    return render_template('staff/top_destinations.html',top_90=top_90,top_365=top_365)


@staff.route('/airline_flights',methods=['GET','POST'])
def airline_flights():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    form=AirlineFlightsForm()
    if form.validate_on_submit():
        first = aliased(Airport)
        second = aliased(Airport)
        earliest = datetime.combine(form.start.data, datetime.min.time())
        latest = datetime.combine(form.finish.data + timedelta(days=1), datetime.min.time())

        airline_name = db.session.query(Airline_Staff).filter(
            Airline_Staff.username == current_user.get_identifier()).first().airline_name

        data = db.session.query(Flight, first, second).join(first, Flight.departs == first.name) \
            .join(second, Flight.arrives == second.name). \
            filter(Flight.departure_time > earliest).filter(Flight.departure_time < latest).\
            filter(Flight.airline_name==airline_name)

        if len(form.source_city.data) > 0:
            data = data.filter(first.city == form.source_city.data)
        if len(form.dest_city.data) > 0:
            data = data.filter(second.city == form.dest_city.data)
        if len(form.source_airport.data) > 0:
            data = data.filter(first.name == form.source_airport.data)
        if len(form.dest_airport.data) > 0:
            data = data.filter(second.name == form.dest_airport.data)
        data = data.all()
        return render_template('staff/view_airline_flights.html',data=data)

    return render_template('staff/airline_flights.html',form=form)

@staff.route('/passenger_list',methods=['GET','POST'])
def passenger_list():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect(url_for('main.index'))
    form=PassengerListForm()
    airline_name = db.session.query(Airline_Staff).filter(
        Airline_Staff.username == current_user.get_identifier()).first().airline_name
    if form.validate_on_submit():
        flight_num=form.flight_num.data
        departure_time=form.departure_time.data
        flight=db.session.query(Flight).filter_by(airline_name=airline_name,flight_num=flight_num,departure_time=departure_time).first()
        if flight is not None:
            data=db.session.query(Purchase.email_customer).join(Ticket,Ticket.ticket_id==Purchase.ticket_id).\
                filter(Ticket.airline_name==airline_name,Ticket.flight_num==flight_num,Ticket.departure_time==departure_time).distinct().all()
            return render_template('staff/view_passenger_list.html',data=data)#TODO make template
    #TODO customer_flights form
    return render_template('staff/passenger_list.html',form=form)

@staff.route('/viewbookingagents',methods=['GET','POST'])
def viewbookingagents():
    staff_airline_table=Airline_Staff.query.filter(Airline_Staff.username==current_user.get_id().split('_')[1:]).first()
    staff_airline=staff_airline_table.airline_name



    agent_purchased_ticket=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name')).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None)

    # top 5 agents based on num of tickets - past month (last 30 days)
    # pas fini
    date_30_days_ago=datetime.now() - timedelta(days=30)
    agent_purchased_ticket_30_days=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name')).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None).filter(Purchase.date>date_30_days_ago)


    return render_template('staff/viewbookingagents.html', \
                            staff_airline=staff_airline,\
                            agent_purchased_ticket_30_days=agent_purchased_ticket_30_days,\
                            agent_purchased_ticket=agent_purchased_ticket)

# TODO - question for prof
# each flight average rating
# all comments and ratings given for that flight by customer
@staff.route('/viewflightratings',methods=['GET','POST'])
def viewflightratings():
    pass
