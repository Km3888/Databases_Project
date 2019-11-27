from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import public
from .. import db
from ..models import Flight,Customer,BookingAgent,Airline_Staff,Airline,load_user,Airport
from .forms import SeeFlightsStatus,OneWayForm,TwoWayForm,FlightTypeForm
from sqlalchemy.orm import aliased

# @public.route('/searchfutureflights',methods=['GET','POST'])
# def searchfutureflights():
#     form=SearchFutureFlights()
#     return render_template('public/searchfutureflights.html',form=form)


@public.route('/searchfutureflights',methods=['GET','POST'])
def searchfutureflights():
    form= FlightTypeForm()
    if form.validate_on_submit():
        type=form.type.data
        if type=='one':
            return redirect('/public/oneway')
        else:
            return redirect('public.twoway')
    return render_template('public/searchfutureflights.html',form=form)
#     form=SearchFutureFlights()
#     if form.validate_on_submit():
#         # where it goes once submitted
#     # unsure how much info to return
#
#         query=Flight.query().join(Airport).filter_by()
#
#         if form.source_airport is not None:
#             query=query.filter_by(airport_name=)
#     # 1 given ('source_city', 'dest_city', 'dest_date')
#     # need to fix date - exclude from where condition for test
#         if form.source_airport is None and form.dest_airport is None and form.return_date is None:
#             query = 'SELECT \
#                 flight_num, \
#                 departure_time, \
#                 departs, \
#                 arrival_time, \
#                 arrives, \
#                 airline_name, \
#                 A.city as Dep, \
#                 B.city as Arr\
#                 FROM \
#                 Flights AS F \
#                 RIGHT OUTER JOIN Airport AS A \
#                 ON \
#                 F.departs = A.name \
#                 RIGHT OUTER JOIN Airport AS B \
#                 ON \
#                 F.arrives = B.name \
#                 WHERE Dep=%s AND Arr=%s'
#
#             from_form = (form['source_city'], form['dest_city'])
#
#
# #AND parse(departure_time)=:date' // ,'date':form.dest_date
#
#         # 2 given ('source_city', 'source_airport', 'dest_city', 'dest_date')
#         # need to fix date - exclude from where condition for test
#         elif form.dest_airport is None and form.return_date is None:
#             query = 'SELECT \
#                 flight_num, \
#                 departure_time, \
#                 departs, \
#                 arrival_time, \
#                 arrives, \
#                 airline_name, \
#                 A.city as Dep, \
#                 B.city as Arr\
#                 FROM \
#                 Flights AS F \
#                 RIGHT OUTER JOIN Airport AS A \
#                 ON \
#                 F.departs = A.name \
#                 RIGHT OUTER JOIN Airport AS B \
#                 ON \
#                 F.arrives = B.name \
#                 WHERE Dep=%s AND Arr=%s AND departs=%s'
#
#             from_form = (form['source_city'], form['dest_city'],form['source_airport'])
#
# #AND parse(departure_time)=:date ' // ,'date':form.dest_date
#
#
#         db.session.execute(query, from_form)
#         data = db.session.fetchall()
#
#         if data is not None:
#         # go to page which displays table results
#             return render_template('public/view_searchfutureflights.html',data=data)
#         #else:
#         # what happens if not submitted
#         # display error message
#         # and redirecto to search flights page
#         #flash('No results found')
#         # or redirect ?
#     return render_template('public/searchfutureflights.html',form=form)



@public.route('/oneway',methods=['GET','POST'])
def oneway():
    form=OneWayForm()
    if form.validate_on_submit():
        first=aliased(Airport)
        second=aliased(Airport)

        small_query=db.session.query(Flight.airline_name)#.join(first,Flight.departs)
        big_query=small_query.join(second,Flight.arrives)#.\
            # filter(second.name==Flight.arrives).filter(first.name==Flight.departs)
        return render_template('public/view_searchfutureflights.html',form=big_query)

        first = Airport.query.filter_by(city=form.source_city)
        if form.source_airport is not None:
            first = first.filter_by(name=form.source_airport)
        second = Airport.query.filter_by(city=form.dest_city)
        if form.source_airport is not None:
            second = second.filter_by(name=form.dest_airport)
        flights=Flight.query
        if form.flight_date is not None:
            flights=flights.filter_by(departure_time=form.flight_date)
            #TODO ^Probably won't work
        joined=flights.join(first,second.name==flights.arrives).join(second,second.name==flights.arrives)
        return render_template('public/view_searchfutureflights.html', data=joined)
    return render_template('auth/login.html', form=form)

#    data="hi"
#    if data=="hi":
#        return render_template('public/view_searchfutureflights.html',data=data)
#    return render_template('public/searchfutureflights.html',form=form)

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
