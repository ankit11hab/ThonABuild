from flask import render_template, url_for, redirect, request
import cloudinary
import cloudinary.uploader
from flask_login.utils import logout_user
from werkzeug.security import generate_password_hash
from application.models import CSVExtract, NotificationHistory, User
from application.forms import AddRowForm, RegistrationForm, LoginForm, NotifyTemplate
from application import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import smtplib
import os
import csv
import io
from datetime import datetime
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
    if current_user.is_authenticated:
        return render_template('account.html')
    else:
        return redirect(url_for('login'))


@app.route("/data")
@login_required
def data():
    if current_user.is_authenticated: 
        return render_template('data.html')
    else:
        return redirect(url_for('login'))

@app.route("/home")
def home():
    if current_user.is_authenticated:
        notif = current_user.history
        day1=day2=day3=day4=day5=0
        for item in notif:
            if (datetime.utcnow() - item.date_time).days==0:
                day5+=1
            if (datetime.utcnow() - item.date_time).days==1:
                day4+=1
            if (datetime.utcnow() - item.date_time).days==2:
                day3+=1
            if (datetime.utcnow() - item.date_time).days==3:
                day2+=1
            if (datetime.utcnow() - item.date_time).days==4:
                day1+=1
        notifdays = {
            'day5':day5,
            'day4':day4,
            'day3':day3,
            'day2':day2,
            'day1':day1
        }
        data = current_user.data
        return render_template('home.html',notif=len(notif),data = data,notifdays=notifdays)
    else:
        return redirect(url_for('login'))

@app.route("/documentation")
def documentation():
    if current_user.is_authenticated:
        return render_template('documentation.html')
    else:
        return redirect(url_for('login'))

@app.route("/custom")
def custom():
    if current_user.is_authenticated:
        return render_template('custom.html')
    else:
        return redirect(url_for('login'))



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
    if current_user.is_authenticated:
        form = NotifyTemplate()
        if form.validate_on_submit():
            print("hello")
            template=form.template.data
            if(request.files['image']):
                uploaded_img = request.files['image']
                cloudinary.config(cloud_name="dmcbeyvr4", api_key="641921374166998",
                                api_secret="q4zM2BjtuVSux3hKkXpG_SqqcnY")
                upload_result = cloudinary.uploader.upload(
                    uploaded_img, folder="buildathon/")
                print(upload_result['secure_url'])
            from twilio.rest import Client 
            notif = NotificationHistory(user_id = current_user.id,type='Event Based',email=form.sendmail.data, sms=form.sendsms.data,whatsapp=form.sendwhatsappmsg.data,message_body = template,period = form.frequency.data,scheduled_date=form.scheduled_date.data,score=form.score.data,event=form.event.data,activity=form.activity.data)
            db.session.add(notif)
            db.session.commit()
            data = current_user.data
            for item in data:
                if item.type=='Event-Based' and item.event_code==form.event.data+' ':
                    txt = item.employee_details
                    email_to = txt.split("; ")[1]
                    mobile_to = txt.split("; ")[2]
                    print(email_to)
                    """ account_sid = ACCOUNT_SID
                    auth_token = AUTH_TOKEN
                    client = Client(account_sid, auth_token) 
                    if form.sendwhatsappmsg.data:
                        if(request.files['image']):
                            whatsappmessage = client.messages.create(
                            from_='whatsapp:'+WHATSAPP_FROM, body=template, media_url=upload_result['secure_url'], to='whatsapp:'+mobile_to)
                        else:
                            whatsappmessage = client.messages.create(
                            from_='whatsapp:'+WHATSAPP_FROM, body=template, to='whatsapp:'+mobile_to)
                    if form.sendsms.data:
                        message = client.messages.create(
                        body=template,
                        messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                        to=mobile_to
                        )
    
                    if form.sendmail.data:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(EMAIL_FROM,PASSWORD)
                        server.sendmail(EMAIL_FROM, email_to, template)
                        server.quit() """

            return redirect(url_for('home'))
        return render_template('submissions/event_form.html',form=form)
    else:
        return redirect(url_for('login'))

@app.route('/score_based', methods=['GET', 'POST'])
def score_based():
    if current_user.is_authenticated:
        form = NotifyTemplate()
        if form.validate_on_submit():
            template=form.template.data
            if(request.files['image']):
                uploaded_img = request.files['image']
                cloudinary.config(cloud_name="dmcbeyvr4", api_key="641921374166998",
                                api_secret="q4zM2BjtuVSux3hKkXpG_SqqcnY")
                upload_result = cloudinary.uploader.upload(
                    uploaded_img, folder="buildathon/")
                print(upload_result['secure_url'])
            from twilio.rest import Client 
            notif = NotificationHistory(user_id = current_user.id,type='Score Based',email=form.sendmail.data, sms=form.sendsms.data,whatsapp=form.sendwhatsappmsg.data,message_body = template,period = form.frequency.data,scheduled_date=form.scheduled_date.data,score=form.score.data,event=form.event.data,activity=form.activity.data)
            db.session.add(notif)
            db.session.commit()
            data = current_user.data
            for item in data:
                if item.type=='Score-Based' and item.event_code==form.score.data+' ':
                    txt = item.employee_details
                    email_to = txt.split("; ")[1]
                    mobile_to = txt.split("; ")[2]
                    print(email_to)
                    """ account_sid = ACCOUNT_SID
                    auth_token = AUTH_TOKEN
                    client = Client(account_sid, auth_token) 
                    if form.sendwhatsappmsg.data:
                        if(request.files['image']):
                            whatsappmessage = client.messages.create(
                            from_='whatsapp:'+WHATSAPP_FROM, body=template, media_url=upload_result['secure_url'], to='whatsapp:'+mobile_to)
                        else:
                            whatsappmessage = client.messages.create(
                            from_='whatsapp:'+WHATSAPP_FROM, body=template, to='whatsapp:'+mobile_to)
                    if form.sendsms.data:
                        message = client.messages.create(
                        body=template,
                        messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                        to=mobile_to
                        )
    
                    if form.sendmail.data:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(EMAIL_FROM,PASSWORD)
                        server.sendmail(EMAIL_FROM, email_to, template)
                        server.quit() """

            return redirect(url_for('home'))
        return render_template('submissions/score_form.html', form=form) 
    else:
        return redirect(url_for('login'))

@app.route('/activity_based', methods = ['GET','POST'])
def activity_based():
    if current_user.is_authenticated:
        form = NotifyTemplate()
        if form.validate_on_submit():
            template=form.template.data
            if(request.files['image']):
                uploaded_img = request.files['image']
                cloudinary.config(cloud_name="dmcbeyvr4", api_key="641921374166998",
                                api_secret="q4zM2BjtuVSux3hKkXpG_SqqcnY")
                upload_result = cloudinary.uploader.upload(
                    uploaded_img, folder="buildathon/")
                print(upload_result['secure_url'])
            from twilio.rest import Client 
            notif = NotificationHistory(user_id = current_user.id,type='Activity Based',email=form.sendmail.data, sms=form.sendsms.data,whatsapp=form.sendwhatsappmsg.data,message_body = template,period = form.frequency.data,scheduled_date=form.scheduled_date.data,score=form.score.data,event=form.event.data,activity=form.activity.data)
            db.session.add(notif)
            db.session.commit()
            data = current_user.data
            for item in data:
                if item.notification_controller==form.activity.data+' ':
                    txt = item.employee_details
                    email_to = txt.split("; ")[1]
                    mobile_to = txt.split("; ")[2]
                    print(email_to)
                    """ account_sid = ACCOUNT_SID
                    auth_token = AUTH_TOKEN
                    client = Client(account_sid, auth_token) 
                    if form.sendwhatsappmsg.data:
                        if(request.files['image']):
                            whatsappmessage = client.messages.create(
                            from_='whatsapp:'+WHATSAPP_FROM, body=template, media_url=upload_result['secure_url'], to='whatsapp:'+mobile_to)
                        else:
                            whatsappmessage = client.messages.create(
                            from_='whatsapp:'+WHATSAPP_FROM, body=template, to='whatsapp:'+mobile_to)
                    if form.sendsms.data:
                        message = client.messages.create(
                        body=template,
                        messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                        to=mobile_to
                        )
    
                    if form.sendmail.data:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(EMAIL_FROM,PASSWORD)
                        server.sendmail(EMAIL_FROM, email_to, template)
                        server.quit() """

            return redirect(url_for('home'))
        return render_template('submissions/activity_form.html',form=form)
    else:
        return redirect(url_for('login'))


@app.route('/history')
def notification_history():
    if current_user.is_authenticated:
        notif = current_user.history
        return render_template('history.html',notif = notif)
    else:
        return redirect(url_for('login'))

@app.route('/history/<int:notif_id>')
def notification_history_id(notif_id):
    if current_user.is_authenticated:
        notif = NotificationHistory.query.get(notif_id)
        return render_template('history_id.html', notif = notif)
    else:
        return redirect(url_for('login'))


@app.route('/conditional_triggers')
def conditional_triggers():
    if current_user.is_authenticated:
        notif = current_user.history
        print(notif)
        score = activity = event = 0
        for item in notif:
            if item.type=='Score Based':
                score+=1
            elif item.type=='Event Based':
                event+=1
            elif item.type=='Activity Based':
                activity+=1
        data = {
            'scoreno': score,
            'eventno':event,
            'activityno': activity
        }
        return render_template('conditional.html',data=data)
    else:
        return redirect(url_for('login'))

uploads_dir = os.path.join(app.instance_path, 'uploads/')


@app.route("/upload_csv", methods=['POST'])
def upload_csv():
    if current_user.is_authenticated:
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
    else:
        return redirect(url_for('login'))

@app.route('/user_table')
def usertable():
    if current_user.is_authenticated:
        data = current_user.data
        return render_template('usertable.html',data=data)
    else:
        return redirect(url_for('login'))

@app.route('/clear')
def cleartable():
    if current_user.is_authenticated:
        data = CSVExtract.query.filter_by(user_id=current_user.id).all()
        for row in data:
            db.session.delete(row)
            db.session.commit() 
        return redirect(url_for('usertable'))
    else:
        return redirect(url_for('login'))

@app.route('/addrow', methods=['GET','POST'])
def addrow():
    if current_user.is_authenticated:
        form = AddRowForm()
        if form.validate_on_submit():
            row = CSVExtract(
                type = form.type.data,
                frequency = form.frequency.data,
                event_date = form.event_date.data,
                due_data = form.due_data.data,
                employee = form.employee .data,
                employee_details = form.employee_details.data,
                event_code = form.event_code.data,
                action_perform = form.action_perform.data,
                notification_controller = form.notification_controller.data,
                notification_event = form.notification_event.data,
                user_id = current_user.id,
            )
            db.session.add(row)
            db.session.commit()
            return redirect(url_for('usertable'))
        return render_template('addrow.html', form=form)
    else:
        return redirect(url_for('login'))


import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler


check = 0
def send_scheduled_notifications():
    global check
    if check==0:
        check+=1
        notifications = NotificationHistory.query.all()
        for notif in notifications:
            if (notif.scheduled_date-datetime.utcnow()).total_seconds() < 19860 and (notif.scheduled_date-datetime.utcnow()).total_seconds() > 0:
                user = User.query.get(notif.user_id)
                data = user.data
                from twilio.rest import Client 
                for item in data:
                    if item.type=='Score-Based' and notif.type=='Score Based' and item.event_code==notif.score:
                        txt = item.employee_details
                        """ email_to = txt.split("; ")[1] """
                        """ mobile_to = txt.split("; ")[2] """
                        """ account_sid = ACCOUNT_SID
                        auth_token = AUTH_TOKEN
                        client = Client(account_sid, auth_token) 
                        if form.sendwhatsappmsg.data:
                            if(request.files['image']):
                                whatsappmessage = client.messages.create(
                                from_='whatsapp:'+WHATSAPP_FROM, body=template, media_url=upload_result['secure_url'], to='whatsapp:'+mobile_to)
                            else:
                                whatsappmessage = client.messages.create(
                                from_='whatsapp:'+WHATSAPP_FROM, body=template, to='whatsapp:'+mobile_to)
                        if form.sendsms.data:
                            message = client.messages.create(
                            body=template,
                            messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                            to=mobile_to
                            )
        
                        if form.sendmail.data:
                            server = smtplib.SMTP('smtp.gmail.com', 587)
                            server.starttls()
                            server.login(EMAIL_FROM,PASSWORD)
                            server.sendmail(EMAIL_FROM, email_to, template)
                            server.quit() """
                    
                    elif item.type=='Event-Based' and notif.type=='Event Based' and item.event_code==notif.event+' ':
                        txt = item.employee_details
                        email_to = txt.split("; ")[1]
                        mobile_to = txt.split("; ")[2]
                        print(email_to)
                        """ account_sid = ACCOUNT_SID
                        auth_token = AUTH_TOKEN
                        client = Client(account_sid, auth_token) 
                        if form.sendwhatsappmsg.data:
                            if(request.files['image']):
                                whatsappmessage = client.messages.create(
                                from_='whatsapp:'+WHATSAPP_FROM, body=template, media_url=upload_result['secure_url'], to='whatsapp:'+mobile_to)
                            else:
                                whatsappmessage = client.messages.create(
                                from_='whatsapp:'+WHATSAPP_FROM, body=template, to='whatsapp:'+mobile_to)
                        if form.sendsms.data:
                            message = client.messages.create(
                            body=template,
                            messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                            to=mobile_to
                            )
        
                        if form.sendmail.data:
                            server = smtplib.SMTP('smtp.gmail.com', 587)
                            server.starttls()
                            server.login(EMAIL_FROM,PASSWORD)
                            server.sendmail(EMAIL_FROM, email_to, template)
                            server.quit() """


                    elif item.type=='Activity-Based' and notif.type=='Activity Based' and item.notification_controller==notif.activity+' ':
                        txt = item.employee_details
                        email_to = txt.split("; ")[1]
                        mobile_to = txt.split("; ")[2]
                        print(email_to)
                        """ account_sid = ACCOUNT_SID
                        auth_token = AUTH_TOKEN
                        client = Client(account_sid, auth_token) 
                        if form.sendwhatsappmsg.data:
                            if(request.files['image']):
                                whatsappmessage = client.messages.create(
                                from_='whatsapp:'+WHATSAPP_FROM, body=template, media_url=upload_result['secure_url'], to='whatsapp:'+mobile_to)
                            else:
                                whatsappmessage = client.messages.create(
                                from_='whatsapp:'+WHATSAPP_FROM, body=template, to='whatsapp:'+mobile_to)
                        if form.sendsms.data:
                            message = client.messages.create(
                            body=template,
                            messaging_service_sid='MG542ab6d1107edc9a4aee705badb89984',
                            to=mobile_to
                            )
        
                        if form.sendmail.data:
                            server = smtplib.SMTP('smtp.gmail.com', 587)
                            server.starttls()
                            server.login(EMAIL_FROM,PASSWORD)
                            server.sendmail(EMAIL_FROM, email_to, template)
                            server.quit() """
    else:
        check=0
                
            



scheduler = BackgroundScheduler()
scheduler.add_job(func=send_scheduled_notifications, trigger="interval", minutes = 1)
scheduler.start()

