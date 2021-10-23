from flask_wtf import FlaskForm
from wtforms.fields.core import StringField
from wtforms.fields.simple import PasswordField, SubmitField,BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from application.models import User

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
    template = TextAreaField('Template', validators = [DataRequired()], render_kw={"placeholder": "Message", "rows":"7"})
    sendwhatsappmsg = BooleanField('Send WhatsApp msg')
    sendmail = BooleanField('Send mail')
    sendsms = BooleanField('Send sms')
    submit = SubmitField('Send')
