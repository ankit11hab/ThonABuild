from application import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    image_file = db.Column(db.String(20),nullable=False,default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    history = db.relationship('NotificationHistory',backref='author',lazy=True)
    data = db.relationship('CSVExtract',backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}' , '{self.image_file}')"


class NotificationHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20),nullable=False)
    scheduled_date = db.Column(db.DateTime, default = datetime.utcnow)
    period = db.Column(db.Integer)
    message_body = db.Column(db.String(500),nullable=False)
    score = db.Column(db.String(100),default='')
    event = db.Column(db.String(100),default='')
    activity = db.Column(db.String(100),default='')
    email = db.Column(db.Boolean,default=False,nullable=False)
    whatsapp = db.Column(db.Boolean,default=False,nullable=False)
    sms = db.Column(db.Boolean,default=False,nullable=False)
    date_time = db.Column(db.DateTime,nullable = False, default = datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"NotificationHistory('{self.id}')"


class CSVExtract(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(500), nullable=False)
    frequency = db.Column(db.String(500), nullable=False)
    event_date = db.Column(db.String(500), nullable=False)
    due_data = db.Column(db.String(500), nullable=False)
    employee = db.Column(db.String(500), nullable=False)
    employee_details = db.Column(db.String(1000), nullable=False)
    event_code = db.Column(db.String(500), nullable=False)
    action_perform = db.Column(db.String(500), nullable=False)
    notification_controller = db.Column(db.String(500), nullable=False)
    notification_event = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"CSV('{self.user_id}', '{self.type}' , '{self.event_date}')"