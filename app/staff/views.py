from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user
from . import staff
from .. import db
from ..models import Purchase,Ticket,Customer,BookingAgent,Airline_Staff,Airline,load_user
# from .forms import
from datetime import datetime,date, timedelta

from .forms import ReportForm

from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import table, column
from sqlalchemy import or_
from sqlalchemy import desc


#TODO - question for prof
    # top 5 based on commission - last month (last 30 days)
@staff.route('/viewbookingagents',methods=['GET','POST'])
def viewbookingagents():
#    staff_airline_table=Airline_Staff.query.filter(Airline_Staff.username==current_user.get_id().split('_')[1:]).first()
    staff_airline_table=Airline_Staff.query.filter(Airline_Staff.username==current_user.get_identifer()).first()

    staff_airline=staff_airline_table.airline_name

    agent_purchased_ticket=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name')).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None)

    # top 5 agents based on num of tickets - past month (last 30 days)
    date_30_days_ago=datetime.now() - timedelta(days=30)
    date_365_days_ago=datetime.now() - timedelta(days=365)
    agent_purchased_ticket_30_days=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name')).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None).filter(Purchase.date>date_30_days_ago)
    grouped_agent_purchased_ticket_30_days=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name')).with_entities(Purchase.email_booking, func.count(Purchase.email_booking).label("count")).group_by(Purchase.email_booking).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None).filter(Purchase.date>date_30_days_ago).order_by(desc("count"))[:5]
    # top 5 based on num of tickets - past year (last 365 days)
    grouped_agent_purchased_ticket_one_year=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name')).with_entities(Purchase.email_booking, func.count(Purchase.email_booking).label("count")).group_by(Purchase.email_booking).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None).filter(Purchase.date>date_365_days_ago).order_by(desc("count"))[:5]
    # order_by("count")[:5]
    #
    commissions_grouped_agent=Purchase.query.join(Ticket, Purchase.ticket_id==Ticket.ticket_id).add_columns(Purchase.email_booking.label('email_booking'), Purchase.date.label('date'), Ticket.airline_name.label('airline_name'), Ticket.price.label('price')).with_entities(Purchase.email_booking.label('email_booking'), (func.sum(Ticket.price)/10).label("total_commission")).group_by(Purchase.email_booking).filter(Ticket.airline_name==staff_airline).filter(Purchase.email_booking!=None).filter(Purchase.date>date_365_days_ago).order_by(desc("total_commission"))[:5]



    return render_template('staff/viewbookingagents.html', \
                            staff_airline=staff_airline,\
                            agent_purchased_ticket_30_days=agent_purchased_ticket_30_days,\
                            agent_purchased_ticket=agent_purchased_ticket,\
                            grouped_agent_purchased_ticket_30_days=grouped_agent_purchased_ticket_30_days,\
                            grouped_agent_purchased_ticket_one_year=grouped_agent_purchased_ticket_one_year,\
                            commissions_grouped_agent=commissions_grouped_agent)

# TODO - question for prof
# each flight average rating
# all comments and ratings given for that flight by customer
@staff.route('/viewflightratings',methods=['GET','POST'])
def viewflightratings():
    staff_airline_table=Airline_Staff.query.filter(Airline_Staff.username==current_user.get_identifer()).first()

    staff_airline=staff_airline_table.airline_name

    ave_ticket_ratings=Ticket.query.join(Purchase, \
                    Ticket.ticket_id==Purchase.ticket_id)\
                    .add_columns(Ticket.airline_name.label('airline_name'),\
                    Ticket.flight_num.label('flight_num'),\
                    Ticket.departure_time.label('departure_time'),\
                    Purchase.rating.label('rating'),\
                    Purchase.comment.label('comment'))\
                    .with_entities(Ticket.flight_num.label('flight_num'),\
                    Ticket.departure_time.label('departure_time'),\
                    func.avg(Purchase.rating).label("ave_rating"))\
                    .group_by(Ticket.flight_num,Ticket.departure_time)\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.rating!=None)

    ticket_rating_comment=Ticket.query.join(Purchase, \
                    Ticket.ticket_id==Purchase.ticket_id)\
                    .add_columns(Ticket.airline_name.label('airline_name'),\
                    Ticket.flight_num.label('flight_num'),\
                    Ticket.departure_time.label('departure_time'),\
                    Purchase.rating.label('rating'),\
                    Purchase.comment.label('comment'))\
                    .with_entities(Ticket.flight_num.label('flight_num'),\
                    Ticket.departure_time.label('departure_time'),\
                    Purchase.rating.label('rating'),\
                    Purchase.comment.label('comment'))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(or_(Purchase.rating!=None, Purchase.comment!=None, Purchase.comment!=''))


    return render_template('staff/viewflightratings.html',\
                            ave_ticket_ratings=ave_ticket_ratings,\
                            ticket_rating_comment=ticket_rating_comment)

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


@staff.route('/staffviewreports',methods=['GET','POST'])
def staffviewreports():
    staff_airline_table=Airline_Staff.query.filter(Airline_Staff.username==current_user.get_identifer()).first()

    staff_airline=staff_airline_table.airline_name

    date_last_month=datetime.now()-timedelta(days=30)
    date_last_year=datetime.now()-timedelta(days=365)

    sold_last_month=Purchase.query.join(Ticket, \
                    Purchase.ticket_id==Ticket.ticket_id)\
                    .add_columns(Ticket.airline_name.label('airline_name'))\
                    .with_entities(func.count(Purchase.ticket_id).label("count"))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.date>date_last_month).first()

    num_sold_last_month=sold_last_month.count

    if num_sold_last_month==None:
        num_sold_last_month=0

    sold_last_year=Purchase.query.join(Ticket, \
                    Purchase.ticket_id==Ticket.ticket_id)\
                    .add_columns(Ticket.airline_name.label('airline_name'))\
                    .with_entities(func.count(Purchase.ticket_id).label("count"))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.date>date_last_year).first()

    num_sold_last_year=sold_last_year.count

    if num_sold_last_year==None:
        num_sold_last_year=0

    query_list_months=intervals_for_num_months(datetime.now(), 12)

    graph_labels=make_list_labels(query_list_months)

    monthly_sums=[]

    for i in range(len(query_list_months)-1):
        default_month=Purchase.query.join(Ticket, \
                        Purchase.ticket_id==Ticket.ticket_id)\
                        .add_columns(Ticket.airline_name.label('airline_name'))\
                        .with_entities(func.count(Purchase.ticket_id).label("count"))\
                        .filter(Ticket.airline_name==staff_airline)\
                        .filter(Purchase.date>=query_list_months[i])\
                        .filter(Purchase.date<query_list_months[i+1]).first()


        default_month_sum=default_month.count
        if default_month_sum==None:
            default_month_sum=0

        monthly_sums.append(default_month_sum)

    form=ReportForm()

    if form.validate_on_submit():
        inputed_start_date=form.start.data
        start_date=date_past=datetime.strptime(str(inputed_start_date), '%Y-%m-%d')
        inputed_end_date=form.end.data
        end_date=date_past=datetime.strptime(str(inputed_end_date), '%Y-%m-%d')

        if end_date<=start_date:
            flash('Invalid date range')

        period_table=Purchase.query.join(Ticket, \
                        Purchase.ticket_id==Ticket.ticket_id)\
                        .add_columns(Ticket.airline_name.label('airline_name'))\
                        .with_entities(func.count(Purchase.ticket_id).label("count"))\
                        .filter(Ticket.airline_name==staff_airline)\
                        .filter(Purchase.date>=start_date)\
                        .filter(Purchase.date<end_date).first()


        period_table_count=period_table.count

        if period_table_count==None:
            period_table_count=0

        query_ranges=intervals_for_range(end_date, start_date)

        ranges_labels=make_list_labels(query_ranges)

        counts=[]

        for i in range(len(query_ranges)-1):

            thrity_days=Purchase.query.join(Ticket, \
                        Purchase.ticket_id==Ticket.ticket_id)\
                        .add_columns(Ticket.airline_name.label('airline_name'))\
                        .with_entities(func.count(Purchase.ticket_id).label("count"))\
                        .filter(Ticket.airline_name==staff_airline)\
                        .filter(Purchase.date>=query_ranges[i])\
                        .filter(Purchase.date<query_ranges[i+1]).first()



            thrity_days_count=thrity_days.count
            if thrity_days_count==None:
                thrity_days_count=0

            counts.append(thrity_days_count)




        return render_template('staff/reports_from_form.html',\
                                period_table_count=period_table_count,\
                                counts=counts,\
                                query_ranges=query_ranges,\
                                ranges_labels=ranges_labels,\
                                max_ranges=max(counts),\
                                start_date=start_date,end_date=end_date)

    return render_template('staff/staffviewreports.html', sold_last_month=sold_last_month,\
                                            num_sold_last_month=num_sold_last_month,\
                                            num_sold_last_year=num_sold_last_year,\
                                            monthly_sums=monthly_sums,\
                                            query_list_months=query_list_months,\
                                            graph_labels=graph_labels,\
                                            max_default=max(monthly_sums),\
                                            form=form)


@staff.route('/revenuecomparison',methods=['GET','POST'])
def revenuecomparison():
    staff_airline_table=Airline_Staff.query.filter(Airline_Staff.username==current_user.get_identifer()).first()
    staff_airline=staff_airline_table.airline_name

    # last month
    date_last_month=datetime.now()-timedelta(days=30)

    cust_last_month=Purchase.query.join(Ticket,\
                    Purchase.ticket_id==Ticket.ticket_id)\
                    .with_entities(func.sum(Ticket.price).label("sum_month_cust"))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.date>date_last_month)\
                    .filter(Purchase.email_booking==None)
    cust_last_month_value=cust_last_month[0][0]

    booking_last_month=Purchase.query.join(Ticket,\
                    Purchase.ticket_id==Ticket.ticket_id)\
                    .with_entities(func.sum(Ticket.price).label("sum_month_book"))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.date>date_last_month)\
                    .filter(Purchase.email_booking!=None)

    booking_last_month_value=booking_last_month[0][0]

    values_month=[cust_last_month_value,booking_last_month_value]

    for i in range(len(values_month)):
        if values_month[i]==None:
            values_month[i]=(0)

    labels=["Direct Revenue","Indirect Revenue (includes Commission)"]

    # last year
    date_last_year=datetime.now()-timedelta(days=365)

    cust_last_year=Purchase.query.join(Ticket,\
                    Purchase.ticket_id==Ticket.ticket_id)\
                    .with_entities(func.sum(Ticket.price).label("sum_year_cust"))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.date>date_last_year)\
                    .filter(Purchase.email_booking==None)
    cust_last_year_value=cust_last_year[0][0]

    booking_last_year=Purchase.query.join(Ticket,\
                    Purchase.ticket_id==Ticket.ticket_id)\
                    .with_entities(func.sum(Ticket.price).label("sum_year_book"))\
                    .filter(Ticket.airline_name==staff_airline)\
                    .filter(Purchase.date>date_last_year)\
                    .filter(Purchase.email_booking!=None)

    booking_last_year_value=booking_last_year[0][0]



    values_year=[cust_last_year_value,booking_last_year_value]
    for i in range(len(values_year)):
        if values_year[i]==None:
            values_year[i]=(0)

    #colors=["#F7464A", "#46BFBD"]
    colors=["#F7464A", "#800000"]
    return render_template('staff/revenuecomparison.html',\
                        booking_last_month=booking_last_month,\
                        cust_last_month=cust_last_month,\
                        cust_last_month_value=cust_last_month_value,\
                        booking_last_month_value=booking_last_month_value,\
                        set_month=zip(values_month, labels, colors),\
                        max_month=max(values_month),\
                        set_year=zip(values_year, labels, colors),\
                        max_year=max(values_year))
