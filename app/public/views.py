from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import public
from .. import db
from ..models import Flight,Customer,BookingAgent,Airline_Staff,Airline,load_user,Airport
from .forms import SeeFlightsStatus,OneWayForm,TwoWayForm,FlightTypeForm
from sqlalchemy.orm import aliased
import datetime


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



@public.route('/oneway',methods=['GET','POST'])
def oneway():
    form=OneWayForm()
    if form.validate_on_submit():
        first=aliased(Airport)
        second=aliased(Airport)
        earliest=datetime.datetime.combine(form.flight_date.data,datetime.datetime.min.time())
        latest=datetime.datetime.combine(form.flight_date.data+datetime.timedelta(days=1),datetime.datetime.min.time())
        data=db.session.query(Flight,first,second).join(first,Flight.departs==first.name) \
            .join(second, Flight.arrives == second.name). \
            filter(Flight.departure_time > earliest).filter(Flight.departure_time < latest)
        if len(form.source_airport.data)>0:
            data=data.filter(first.city==form.source_airport)
        if len(form.dest_airport.data)>0 :
            data=data.filter(second.city==form.dest_airport)
        data=data.all()
        return render_template('public/view_searchfutureflights.html',data=data)
    return render_template('auth/login.html', form=form)


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
