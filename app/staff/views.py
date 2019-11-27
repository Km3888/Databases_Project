from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user
from . import staff
from .. import db
from ..models import Customer,BookingAgent,Airline_Staff,Airline,load_user
# from .forms import
