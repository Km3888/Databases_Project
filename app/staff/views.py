from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user
from . import staff
from .. import db
from ..models import Purchase,Ticket,Customer,BookingAgent,Airline_Staff,Airline,load_user
# from .forms import
from datetime import datetime,date, timedelta


#TODO - question for prof
    # top 5 based on num of tickets - past month (last 30 days)
    # top 5 based on num of tickets - past year (last 365 days)
    # top 5 based on commission - last month (last 30 days)
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
