from flask import render_template, url_for, redirect, request
from flask_login.utils import logout_user
from werkzeug.security import generate_password_hash
from application.models import CSVExtract, NotificationHistory, User
from application.forms import RegistrationForm, LoginForm, NotifyTemplate
from application import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import smtplib
import os
import csv
import io
from werkzeug.utils import secure_filename
from io import TextIOWrapper
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")
SMS_TO = os.getenv("SMS_TO")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")



@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route("/account")
@login_required
def account():
    return render_template('account.html')


@app.route("/data")
@login_required
def data():
    return render_template('data.html')

@app.route("/home")
def home():
    notif = current_user.history
    return render_template('home.html',notif=len(notif))

@app.route("/documentation")
def documentation():
    return render_template('documentation.html')

@app.route("/custom")
def custom():
    return render_template('custom.html')



@app.route("/login", methods = ['GET','POST'])
@app.route("/", methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect('home')
    return render_template('login.html', form=form)

@app.route("/register", methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect('home')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
    
@app.route('/event_based', methods = ['GET','POST'])
def event_based():
    form = NotifyTemplate()
    if form.validate_on_submit():
        template=form.template.data
        from twilio.rest import Client 
        notif = NotificationHistory(user_id = current_user.id,type='Event Based',email=form.sendmail.data, sms=form.sendsms.data,whatsapp=form.sendwhatsappmsg.data,message_body = template)
        db.session.add(notif)
        db.session.commit()
        account_sid = ACCOUNT_SID
        auth_token = AUTH_TOKEN
        client = Client(account_sid, auth_token) 
        if form.sendwhatsappmsg.data:
            whatsappmessage = client.messages.create(from_='whatsapp:'+WHATSAPP_FROM, body= template, to='whatsapp:'+WHATSAPP_TO) 
        if form.sendsms.data:
            message = client.messages.create(
                     body=template,
                     messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                     to=SMS_TO
                 )
 
        if form.sendmail.data:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_FROM,PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, template)
            server.quit()

        return redirect(url_for('home'))
    return render_template('submissions/event_form.html',form=form)

@app.route('/score_based', methods = ['GET','POST'])
def score_based():
    form = NotifyTemplate()
    if form.validate_on_submit():
        template=form.template.data
        from twilio.rest import Client 
        notif = NotificationHistory(user_id = current_user.id,type='Score Based',email=form.sendmail.data, sms=form.sendsms.data,whatsapp=form.sendwhatsappmsg.data,message_body = template)
        db.session.add(notif)
        db.session.commit()
        account_sid = ACCOUNT_SID
        auth_token = AUTH_TOKEN
        client = Client(account_sid, auth_token) 
        if form.sendwhatsappmsg.data:
            whatsappmessage = client.messages.create(from_='whatsapp:'+WHATSAPP_FROM, body= template, to='whatsapp:'+WHATSAPP_TO) 
        if form.sendsms.data:
            message = client.messages.create(
                     body=template,
                     messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                     to=SMS_TO
                 )
 
        if form.sendmail.data:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_FROM,PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, template)
            server.quit()

        return redirect(url_for('home'))
    return render_template('submissions/score_form.html',form=form)    

@app.route('/activity_based')
def activity_based():
    return render_template('submissions/score_form.html')


@app.route('/history')
def notification_history():
    notif = current_user.history
    return render_template('history.html',notif = notif)

@app.route('/history/<int:notif_id>')
def notification_history_id(notif_id):
    notif = NotificationHistory.query.get(notif_id)
    return render_template('history_id.html', notif = notif)


@app.route('/conditional_triggers')
def conditional_triggers():
    return render_template('conditional.html')

uploads_dir = os.path.join(app.instance_path, 'uploads/')


@app.route("/upload_csv", methods=['POST'])
def upload_csv():
    uploaded_file = request.files['file']
    stream = io.StringIO(
        uploaded_file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    for row in csv_input:
        data = CSVExtract(
            type = row[0],
            frequency = row[1],
            event_date = row[2],
            due_data = row[3],
            employee = row[4],
            employee_details = row[5],
            event_code = row[6],
            action_perform = row[7],
            notification_controller = row[8],
            notification_event = row[9],
            user_id = current_user.id,
        )
        db.session.add(data)
        db.session.commit()


    # Uploading the file 
    uploaded_file.save(os.path.join(
        uploads_dir, secure_filename(uploaded_file.filename)))

    return redirect(url_for('home'))

@app.route('/user_table')
def usertable():
    data = current_user.data
    return render_template('usertable.html',data=data)

@app.route('/clear')
def cleartable():
    data = CSVExtract.query.filter_by(user_id=current_user.id).all()
    for row in data:
        db.session.delete(row)
        db.session.commit() 
    return redirect(url_for('usertable'))