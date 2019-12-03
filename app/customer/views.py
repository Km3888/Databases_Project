from flask import render_template, redirect, request, url_for, flash
# session
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import customer
from .. import db
from .forms import PurchaseFlightForm,ConfirmPurchaseForm
from ..models import Customer,BookingAgent,Airline_Staff,Airline,load_user,Flight, Ticket,Purchase,Airplane

from datetime import datetime,date, timedelta

from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import table, column



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

# for parsing by month
def return_starts_int(end_date, start_date=None, num_months=None):
    l_to_reverse=[]
    d=end_date
    last=str(d.year)+'-'+str(d.month)+'-01'
    last_start=datetime.strptime(last, '%Y-%m-%d')
    l_to_reverse.append(last_start)

    # l_to_reverse.append('one')
    list_of_dates=[]

    year=int(d.year)
    month=int(d.month)
    end='-01'

    first_date=str(month)+'-'+str(year)

    list_of_dates.append(first_date)

    if num_months!=None:
        count=1
        while count<num_months:
            if month!=1:
                most_recent=str(year)+'-'+str(month-1)+'-01'
                #print(most_recent)
                date_most_recent=datetime.strptime(most_recent, '%Y-%m-%d')
                print(date_most_recent)
                l_to_reverse.append(date_most_recent)
                month-=1
                str_date=str(month)+'-'+str(year)
                list_of_dates.append(str_date)
                count+=1
            elif month==1:
                year-=1
                month=13
                most_recent=str(year)+'-'+str(month-1)+'-01'
                #print(most_recent)
                date_most_recent=datetime.strptime(most_recent, '%Y-%m-%d')
                print(date_most_recent)
                l_to_reverse.append(date_most_recent)
                month-=1
                str_date=str(month)+'-'+str(year)
                list_of_dates.append(str_date)
                count+=1


    l_to_reverse.reverse()
    list_of_dates.reverse()
    return [l_to_reverse,list_of_dates]




#TODO
@customer.route('/spending',methods=['GET','POST'])
def spending():
    # default part
    # date one year ago
    one_year_ago = datetime.now() - timedelta(days=365)

    # all purchases
    purchased_ticket=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_customer.label('email_customer'), Purchase.date.label('date'), Ticket.price.label('price')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:])
    # test of sum for all purchases
    total_overall=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).with_entities(func.sum(Ticket.price).label('all_sum')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:]).first()
    total_overall_value=total_overall.all_sum

    if total_overall_value==None:
        total_overall_value=0
        total_overall=0

    # table purchases within past year
    default_total_table=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_customer.label('email_customer'), Purchase.date.label('date'), Ticket.price.label('price')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:]).filter(Purchase.date>one_year_ago)
    # sum for all purchases last year
    default_total_sum_table=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).with_entities(func.sum(Ticket.price).label('all_sum')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:]).filter(Purchase.date>one_year_ago).first()
    default_total_sum=default_total_sum_table.all_sum

    if default_total_sum==None:
        default_total_sum=0

    default_list_start_months=return_starts_int(datetime.now(), None, num_months=6)

    sums=[]

    for i in range(len(default_list_start_months[0])-1):
        default_month=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).with_entities(func.sum(Ticket.price).label('all_sum')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:]).filter(Purchase.date>=default_list_start_months[0][i]).filter(Purchase.date<default_list_start_months[0][i+1]).first()
        default_month_sum=default_month.all_sum
        if default_month_sum==None:
            default_month_sum=0
        sums.append(default_month_sum)

    last_month=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).with_entities(func.sum(Ticket.price).label('all_sum')).filter(Purchase.email_customer==current_user.get_id().split('_')[1:]).filter(Purchase.date>=default_list_start_months[0][(len(default_list_start_months[0])-1)]).first()
    last_month_sum=last_month.all_sum
    if last_month_sum==None:
        last_month_sum=0
    sums.append(last_month_sum)

    list_of_dates=default_list_start_months[1]

    # str_list_of_dates=json.dumps(list_of_dates)
    # for i in list_of_dates:
    #     new_i=""
    #     for letter in i:
    #         new_i+=str(letter)+" "
    #     str_list_of_dates.append(new_i)




    rows_for_graph = []

    # for i in list_of_dates:
    #     i.replace("\'", "\"")


    for i in range(len(sums)):
        pair=[list_of_dates[i],int(sums[i])]
        rows_for_graph.append(pair)
    # rows_for_graph=json.dumps(rows_for_graph)



#users.query.join(friendships, users.id==friendships.user_id).add_columns(users.userId, users.name, users.email, friends.userId, friendId).filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)
    return render_template('customer/spending.html',default_total_sum=default_total_sum,\
                            default_total_table=default_total_table,\
                            purchased_ticket=purchased_ticket,\
                            sums=sums,\
                            list_of_dates=list_of_dates,\
                            rows_for_graph=rows_for_graph,\
                            total_overall_value=total_overall_value)

    #pass
