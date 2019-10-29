from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

class BookingAgent(UserMixin,db.Model):
    __tablename__='agent'
    email= db.Column(db.String(64),primary_key=True)
    password_hash = db.Column(db.String(128))
    booking_agent_id= db.Column(db.Integer)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User %r>'%self.email

class Role(db.Model):
    __tablename__='agent'
    id=db.Column(db.Integer,primary_key=True)

def load_user(user_id):
    return User.query.get(int(user_id))
