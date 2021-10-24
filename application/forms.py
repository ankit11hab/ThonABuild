from flask_wtf import FlaskForm
from wtforms.fields.core import DateTimeField, SelectField, StringField
from wtforms.fields.simple import PasswordField, SubmitField,BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from application.models import User
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('Password', validators = [DataRequired()])

    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username already exists')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class NotifyTemplate(FlaskForm):
    scheduled_date =  DateTimeField('Scheduled Date',format='%Y-%m-%dT%H:%M')
    frequency = SelectField(
        u'Frequency',
        choices = [('Once', 'Once'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')]
    )
    template = TextAreaField('Template', validators = [DataRequired()], render_kw={"placeholder": "Message", "rows":"7"})
    score = StringField('Score', render_kw={"placeholder": "Score"})
    event = StringField('Score', render_kw={"placeholder": "Event"})
    activity = StringField('Score', render_kw={"placeholder": "Activity"})
    sendwhatsappmsg = BooleanField('Send WhatsApp msg')
    image = FileField('Attach Image', validators=[
                      FileAllowed(['jpg', 'png'], 'Images only!')])
    sendmail = BooleanField('Send mail')
    sendsms = BooleanField('Send sms')
    submit = SubmitField('Send')

class AddRowForm(FlaskForm):
    type = StringField('Type', render_kw={"placeholder": "Type"})
    frequency = StringField('Frequency', render_kw={"placeholder": "Frequency"})
    event_date = StringField('Event Date', render_kw={"placeholder": "Event date"})
    due_data = StringField('Due date', render_kw={"placeholder": "Due date"})
    employee = StringField('Employee', render_kw={"placeholder": "Employee"})
    employee_details = StringField('Employee details', render_kw={"placeholder": "Employee details"})
    event_code = StringField('Event code', render_kw={"placeholder": "Event code"})
    action_perform = StringField('Action perform', render_kw={"placeholder": "Action perform"})
    notification_controller = StringField('Notification controller', render_kw={"placeholder": "Notification controller"})
    notification_event = StringField('Notification event', render_kw={"placeholder": "Notification event"})