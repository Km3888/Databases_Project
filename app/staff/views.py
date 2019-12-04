from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user
from . import staff
from .. import db
from ..models import Purchase,Ticket,Customer,BookingAgent,Airline_Staff,Airline,load_user,Flight,Airplane,Airport
from datetime import datetime,date, timedelta
from .forms import ChangeStatusForm,AddAirplaneForm,AddFlightForm

#TODO - question for prof
    # top 5 based on num of tickets - past month (last 30 days)
    # top 5 based on num of tickets - past year (last 365 days)
    # top 5 based on commission - last month (last 30 days)

@staff.route('/change_flight_status',methods=['GET','POST'])
def change_flight_status():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect('main.index')
    form=ChangeStatusForm()
    if form.validate_on_submit():
        airline_name=db.session.query(Airline_Staff).filter(Airline_Staff.username==current_user.get_identification()).first().airline_name
        flight_num=form.flight_num.data
        departure_date=form.departure_time.data
        flight=db.session.query(Flight).filter_by(airline_name=airline_name,flight_num=flight_num,departure_date=departure_date).first()
        if flight is not None:
            flight.status=form.new_status.data
            db.session.commit()
            flash('Updated status to:'+form.new_status.data)
            redirect('main.index')
        flash('Could not find this flight for your airline')
    return render_template('staff/change_flight_status.html',form=form)

@staff.route('/add_airplane',methods=['GET','POST'])
def add_airplane():
    #TODO add_airplane form
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect('main.index')
    form=AddAirplaneForm()
    if form.validate_on_submit():
        airline_name = db.session.query(Airline_Staff).filter(Airline_Staff.username == current_user.get_identification()).first().airline_name
        plane_id=form.airplane_id.data
        seat_count=form.seat_count.data
        plane=db.session.query(Airplane).filter_by(airline_name=airline_name,plane_id=plane_id).first()
        if plane is None:
            new_plane=Airplane(airline_name=airline_name,plane_id=plane_id,seat_count=seat_count)
            db.session.add(new_plane)
            db.session.commit()
        flash('There is already a flight with this ID in your airline')
    return render_template('staff/add_airplane.html',form=form)

@staff.route('/add_flight',methods=['GET','POST'])
def add_flight():
    if not current_user.is_authenticated or not current_user.get_type()=='staff':
        flash('You must be logged in as an airline staff for this action')
        return redirect('main.index')
    form=AddFlightForm()
    if form.validate_on_submit():
        airline_name = db.session.query(Airline_Staff).filter(Airline_Staff.username == current_user.get_identification()).first().airline_name
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
            return render_template('add_airplane.html')
        airplane=db.session.query(Airplane).filter_by(airline_name=airline_name,airplane_id=airplane_id).first()
        if airplane is not None:
            flash('There is no airplane with this id in your airline')
            return render_template('add_airplane.html')
        departs_airport=db.session.query(Airport).filter_by(name=departs).first()
        if departs_airport is None:
            flash('There is no airport with this name(departure airport)')
            return render_template('add_airplane.html')
        arrives_airport = db.session.query(Airport).filter_by(name=arrives).first()
        if arrives_airport is None:
            flash('There is no airport with this name(departure airport)')
            return render_template('add_airplane.html')
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
        return redirect('main.index')

    return render_template('add_airplane.html')

@staff.route('/add_airport',methods=['GET','POST'])
def add_aiport():
    pass

@staff.route('/frequent_customers',methods=['GET','POST'])
def frequent_customers():
    pass

@staff.route('/top_destinations',methods=['GET','POST'])
def top_destinations():
    pass

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
