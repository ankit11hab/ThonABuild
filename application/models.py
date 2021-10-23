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

    def __repr__(self):
        return f"User('{self.username}', '{self.email}' , '{self.image_file}')"


class NotificationHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20),nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    period = db.Column(db.Integer)
    message_body = db.Column(db.String(500),nullable=False)
    email = db.Column(db.Boolean,default=False,nullable=False)
    whatsapp = db.Column(db.Boolean,default=False,nullable=False)
    sms = db.Column(db.Boolean,default=False,nullable=False)
    date_time = db.Column(db.DateTime,nullable = False, default = datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"NotificationHistory('{self.id}')"

