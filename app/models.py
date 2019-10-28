from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class BookingAgent(db.Model):
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


