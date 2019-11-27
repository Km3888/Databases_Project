from flask import render_template
from . import main
from flask_login import current_user
from .. import db
@main.route('/')
def index():
    if current_user.is_authenticated:
        user_type=current_user.get_type()
        print('user type:',user_type)
        if user_type=='agent':
            return render_template('agent_index.html')
        if user_type=='customer':
            return render_template('customer_index.html')
        if user_type=='staff':
            return render_template('staff_index.html')
    return render_template('index.html')

