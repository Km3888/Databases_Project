from flask import render_template, redirect, request, url_for, flash,session
# session
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import customer
from .. import db
from .forms import SpendingForm,PurchaseFlightForm,ConfirmPurchaseForm,CompletedFlights
from ..models import Customer,BookingAgent,Airline_Staff,Airline,load_user,Flight, Ticket,Purchase,Airplane

from datetime import datetime,date, timedelta

from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import table, column

import json



@customer.route('/myflights',methods=['GET','POST'])
def myflights():
    if not current_user.is_authenticated or not current_user.get_type()=='customer':
        return redirect(url_for('main.index'))
    data=db.session.query(Ticket,Purchase,Flight).join(Purchase,\
        Ticket.ticket_id==Purchase.ticket_id).join(Flight, Ticket.airline_name==Flight.airline_name)\
        .filter(Purchase.email_customer==current_user.get_identifier()).filter(Flight.departure_time >= datetime.now()).filter(Ticket.flight_num==Flight.flight_num).\
        filter(Ticket.departure_time==Flight.departure_time)
    return render_template('customer/passenger_list.html',data=data)

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
    # display completed flights of that user on the form page
    #completedflights=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Ticket.airline_name, Ticket.flight_num, Ticket.departure_time)   Purchase.email_customer.label('email_customer'), Purchase.date.label('date'), Ticket.price.label('price')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:])
    # display past ratings and comments

    if not current_user.is_authenticated or not current_user.get_type()=='customer':
        return redirect(url_for('main.index'))

    past_flights=Ticket.query.join(Purchase, Ticket.ticket_id==Purchase.ticket_id)\
                            .join(Flight, Ticket.airline_name==Flight.airline_name)\
                            .add_columns(Ticket.airline_name.label("airline_name"),\
                            Ticket.ticket_id.label("ticket_id"),\
                            Ticket.flight_num.label("flight_num"),\
                            Ticket.departure_time.label("departure_time"),\
                            Purchase.rating.label("rating"),\
                            Purchase.comment.label("comment"))\
                            .filter(Flight.arrival_time<datetime.now())\
                            .filter(Purchase.email_customer==current_user.get_identifier())\
                            .filter(Ticket.departure_time==Flight.departure_time)\
                            .filter(Ticket.flight_num==Flight.flight_num)
    #result=past_flights.ticket_id


    form = CompletedFlights()
    if form.validate_on_submit():

        if form.rating.data is not None and (form.rating.data<0 or form.rating.data>5):
            flash('Please enter a rating between 0 and 5')
            #return render_template('customer/selecttorate.html', past_flights=past_flights, form=form)

        airline_name=form.airline_name.data
        flight_num=form.flight_num.data
        departure_time=form.departure.data



        check=db.session.query(Purchase)\
                        .join(Ticket, Purchase.ticket_id==Ticket.ticket_id)\
                        .join(Flight, Ticket.flight_num==Flight.flight_num)\
                        .filter(Ticket.airline_name==Flight.airline_name)\
                        .filter(Ticket.departure_time==Flight.departure_time)\
                        .filter(Purchase.email_customer==current_user.get_identifier())\
                        .filter(Flight.arrival_time<datetime.now())\
                        .filter(Flight.airline_name==airline_name)\
                        .filter(Flight.flight_num==flight_num)\
                        .filter(Flight.departure_time==departure_time).first()

        # flight=db.session.query(Flight).filter_by(airline_name=airline_name,flight_num=flight_num,departure_time=departure_time).first()
        # if flight is not None:
        #     flight.status=form.new_status.data
        #     db.session.commit()
        #     flash('Updated status to:'+form.new_status.data)
        #
        # purchased_flight=db
        #
        if check is not None:

            tick=check.ticket_id
            purchased_flight=db.session.query(Purchase).filter_by(ticket_id=tick).first()
            if form.rating.data is not None and form.rating.data>0 and form.rating.data<=5:
                purchased_flight.rating=form.rating.data
                db.session.commit()
                flash('Rating Updated to '+str(form.rating.data))
            else:
                flash('Rating Not Updated')
            if form.comment.data is not None:
                purchased_flight.comment=form.comment.data
                db.session.commit()
                flash('Comment Updated to '+form.comment.data)



        # db.session.add(check)
        # db.commit()
        # session['ticket_id']=ticket_id


        #
        # if check is not None:
        #
        #
        #     return redirect('rate')
        #     # create new form to comment
        #     # do return redirect to page to comment
        #
        # flash('Flight not completed')
            return redirect(url_for('main.index'))


    return render_template('customer/selecttorate.html', past_flights=past_flights, form=form)


## for parsing by 30 days



## for parsing by 30 days
def intervals_for_range(end_date, start_date):
    # full end date aka next day
    end_date=end_date+timedelta(days=1)
    clean_end_date=str(end_date.year)+'-'+str(end_date.month)+'-'+str(end_date.day)
    clean_end_date=datetime.strptime(clean_end_date, '%Y-%m-%d')

    list_for_query_comparisons=[]

    clean_start_date=str(start_date.year)+'-'+str(start_date.month)+'-'+str(start_date.day)

    clean_start_date=datetime.strptime(clean_start_date, '%Y-%m-%d')

    list_for_query_comparisons.append(clean_start_date)

    days=(clean_end_date-clean_start_date).days

    full_months=int(days//30)

    for i in range(full_months):
        clean_start_date+=timedelta(days=31)
        list_for_query_comparisons.append(clean_start_date)

    if list_for_query_comparisons[-1]!=clean_end_date:
        list_for_query_comparisons.append(clean_end_date)


    return list_for_query_comparisons

def intervals_for_num_months(end_date, num_months):
    # full end date aka next day

    end_date=end_date+timedelta(days=1)
    clean_end_date=str(end_date.year)+'-'+str(end_date.month)+'-'+str(end_date.day)
    clean_end_date=datetime.strptime(clean_end_date, '%Y-%m-%d')

    list_for_query_comparisons=[]
    list_for_query_comparisons.append(clean_end_date)

    year=clean_end_date.year
    month=clean_end_date.month
    day=clean_end_date.day

    count=0
    while count<num_months:
        if month!=1:

            past=str(year)+'-'+str(month-1)+'-'+str(day)
            date_past=datetime.strptime(past, '%Y-%m-%d')

            list_for_query_comparisons.append(date_past)

            month-=1
            count+=1
        elif month==1:
            year-=1
            month=13
            past=str(year)+'-'+str(month-1)+'-'+str(day)

            date_past=datetime.strptime(past, '%Y-%m-%d')

            list_for_query_comparisons.append(date_past)
            month-=1
            count+=1

    list_for_query_comparisons.reverse()

    return list_for_query_comparisons

def make_list_labels(times_list):

    intervals=[]

    if len(times_list)==2:
        interval=""
        start=str(times_list[0])
        interval+=start[:10]
        interval+=' to '
        end=times_list[1]-timedelta(days=1)

        end=str(end)
        interval+=end[:10]
        intervals.append(interval)


    else:

        for i in range(len(times_list)-1):
            interval=""
            start=str(times_list[i])
            interval+=start[:10]
            interval+=' to '
            end=times_list[i+1]-timedelta(days=1)
            end=str(end)
            interval+=end[:10]
            intervals.append(interval)


    return intervals

@customer.route('/spending',methods=['GET','POST'])
def spending():
    # default part
    # date one year ago
    one_year_ago = datetime.now() - timedelta(days=365)

    # table purchases within past year
    default_total_table=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id)\
                                .add_columns(Purchase.email_customer.label('email_customer'), Purchase.date.label('date'), Ticket.price.label('price'))\
                                .filter(Purchase.email_customer==current_user.get_id().split('_')[1:])\
                                .filter(Purchase.date>one_year_ago)
    # sum for all purchases last year
    default_total_sum_table=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).with_entities(func.sum(Ticket.price).label('all_sum')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:]).filter(Purchase.date>one_year_ago).first()
    default_total_sum=default_total_sum_table.all_sum

    if default_total_sum==None:
        default_total_sum=0

    query_list_months=intervals_for_num_months(datetime.now(), 6)

    graph_labels=make_list_labels(query_list_months)

    monthly_sums=[]

    for i in range(len(query_list_months)-1):
        default_month=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id)\
                                .with_entities(func.sum(Ticket.price).label('all_sum'))\
                                .filter(Purchase.email_customer==current_user.get_id().split('_')[1:])\
                                .filter(Purchase.date>query_list_months[i])\
                                .filter(Purchase.date<query_list_months[i+1]).first()
        default_month_sum=default_month.all_sum
        if default_month_sum==None:
            default_month_sum=0

        monthly_sums.append(default_month_sum)







    form=SpendingForm()

    if form.validate_on_submit():
        inputed_start_date=form.start.data
        start_date=date_past=datetime.strptime(str(inputed_start_date), '%Y-%m-%d')
        inputed_end_date=form.end.data
        end_date=date_past=datetime.strptime(str(inputed_end_date), '%Y-%m-%d')

        if end_date<=start_date:
            flash('Invalid date range')


        # sum for all purchases from that period
        period_table=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id)\
                                .with_entities(func.sum(Ticket.price).label('all_sum'))\
                                .filter(Purchase.email_customer==current_user.get_id().split('_')[1:])\
                                .filter(Purchase.date>=start_date)\
                                .filter(Purchase.date<=end_date).first()


        period_table_sum=period_table.all_sum

        if period_table_sum==None:
            period_table_sum=0
        #query_ranges=intervals_for_range(end_date, start_date-timedelta(seconds=1))

        query_ranges=intervals_for_range(end_date, start_date)

        ranges_labels=make_list_labels(query_ranges)

        sums=[]

        for i in range(len(query_ranges)-1):
            thrity_days=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id)\
                                    .with_entities(func.sum(Ticket.price).label('all_sum'))\
                                    .filter(Purchase.email_customer==current_user.get_id().split('_')[1:])\
                                    .filter(Purchase.date>=query_ranges[i])\
                                    .filter(Purchase.date<query_ranges[i+1]).first()
            thrity_days_sums=thrity_days.all_sum
            if thrity_days_sums==None:
                thrity_days_sums=0

            sums.append(thrity_days_sums)









        return render_template('customer/spending_from_form.html',\
                                period_table_sum=period_table_sum,\
                                sums=sums,\
                                query_ranges=query_ranges,\
                                ranges_labels=ranges_labels,\
                                max_ranges=max(sums),\
                                start_date=start_date,end_date=end_date)


    return render_template('customer/spending.html',\
                            default_total_sum=default_total_sum,\
                            monthly_sums=monthly_sums,\
                            query_list_months=query_list_months,\
                            graph_labels=graph_labels,\
                            max_default=max(monthly_sums),\
                            form=form)
