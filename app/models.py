from . import db,login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin,AnonymousUserMixin


#TODO flesh out permissions
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class BookingAgent(UserMixin,db.Model):
    __tablename__='agent'

    email=db.Column(db.String(64),primary_key=True)
    #no longer email
    password_hash = db.Column(db.String(128))
    booking_agent_id= db.Column(db.Integer)

    Purchase=db.relationship('Purchase',backref='agent')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return self.email

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def verify_id(self,id):
        return int(id)==self.booking_agent_id

    def __repr__(self):
        return '<User %r>'%self.email

class Customer(UserMixin,db.Model):
    __tablename__='customer'

    email=db.Column(db.String(64),primary_key=True)
    name=db.Column(db.String(64))
    password_hash=db.Column(db.String(128))

    building_number=db.Column(db.Integer)
    street=db.Column(db.String(64))
    city=db.Column(db.String(64))
    state=db.Column(db.String(32))

    phone_num=db.Column(db.String(64))
    passport_num=db.Column(db.String(64))
    passport_expiration=db.Column(db.DateTime)
    passport_country=db.Column(db.String(64))
    DOB=db.Column(db.DateTime)

    Purchase=db.relationship('Purchase',backref='customer')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.email

    def __repr__(self):
        return '<User %r>' % self.email

class Airline_Staff(UserMixin,db.Model):
    __tablename__='airline_staff'
    username=db.Column(db.String(64),primary_key=True)
    password_hash=db.Column(db.String(128))
    first_name=db.Column(db.String(64))
    last_name=db.Column(db.String(64))
    date_of_birth=db.Column(db.DateTime)
    airline_name=db.Column(db.String(64),db.ForeignKey('airline.name'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.email

    def __repr__(self):
        return '<User %r>' % self.email

class Airline(db.Model):
    __tablename__='airline'
    name=db.Column(db.String(64),primary_key=True)
    airplanes=db.relationship('Airplane',backref='plane')
    staff=db.relationship('Airline_Staff',backref='airline')


class Airplane(db.Model):
    __tablename__='airplane'
    airline_name=db.Column(db.String(64),db.ForeignKey('airline.name'),primary_key=True)
    id=db.Column(db.String(64))



class Flight(db.Model):
    __tablename__='flight'
    airline_name=db.Column(db.String(64),primary_key=True)
    flight_num=db.Column(db.Integer,primary_key=True)
    departure_time=db.Column(db.DateTime,primary_key=True)
    arrival_time=db.Column(db.DateTime)
    price=db.Column(db.Integer)
    status=db.Column(db.String(64))
    arrives=db.Column(db.String(64),db.ForeignKey('airport.name'))
    departs=db.Column(db.String(64),db.ForeignKey('airport.name'))
    airplane_id=db.Column(db.String(64))

    __table_args__ = (
        db.ForeignKeyConstraint(['airline_name', 'airplane_id'],
                                ['airplane.airline_name', 'airplane.id'],
                                name='constraint_flight_airline'),
    )

class Airport(db.Model):
    __tablename__='airport'
    name=db.Column(db.String(64),primary_key=True)
    city=db.Column(db.String(64))

    flight_arrival=db.relationship('Flight',backref='airport',foreign_keys=[Flight.arrives],lazy='dynamic')
    flight_departure=db.relationship('Flight',backref='other_airport',foreign_keys=[Flight.departs],lazy='dynamic')

class Ticket(db.Model):
    __tablename__='ticket'
    ticket_id=db.Column(db.String(64),primary_key=True)
    airline_name=db.Column(db.String(64))
    flight_num=db.Column(db.String(64))
    departure_time=db.Column(db.DateTime)

    purchases=db.relationship('Purchase',backref='ticket')
    __table_args__ = (
        db.ForeignKeyConstraint(['airline_name','flight_num','departure_time'],
                                ['flight.airline_name','flight.flight_num','flight.departure_time'])
    ,)
    #how to handle backref for super fucked foreign key constraints



class Purchase(db.Model):
    __tablename__='purchase'
    ticket_id=db.Column(db.String(64),db.ForeignKey('ticket.ticket_id'),primary_key=True)
    email_booking=db.Column(db.String(64),db.ForeignKey('agent.email'),primary_key=True)
    email_customer=db.Column(db.String(64),db.ForeignKey('customer.email'),primary_key=True)
    rating=db.Column(db.Integer())
    comment=db.Column(db.String(300))
    date=db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    t=user_id.split('_')[0]
    if t=='agent':
        return BookingAgent.query.filter_by(email=user_id).first()
    if t=='customer':
        return Customer.query.filter_by(email=user_id).first()
    if t=='staff':
        return Airline_Staff.query.filter_by(username=user_id).first()
    raise Exception('SOMETHING HAPPENED')
