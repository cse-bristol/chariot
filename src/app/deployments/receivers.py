#from deployments.signals import sensor_reading_recieved
#from django.dispatch import reciever
from chariot.influx import influx
from deployments.models import Deployment, DeploymentSensor
from datetime import timedelta, datetime, time
import smtplib
from email.mime.text import MIMEText
import urllib.request
import urllib.parse

#@reciever(sensor_reading_recieved)
def receive_notification(sender, deployment_pk, sensor, temp):
    #Get thermal bounds for sensor
    try:
        deployment = Deployment.objects.get(pk=deployment_pk)
        s = DeploymentSensor.objects.get(
            deployment=deployment_pk,
            sensor=sensor)

        channel_id = "TEMP"

        notification_type = None
        if deployment.safeguards_on == True and temp < s.safeguard_temp_lower and s.notifications_on == True:
            notification_type = "BELOW MIN TEMP."

        elif deployment.safeguards_on == True and temp >  s.safeguard_temp_upper and s.notifications_on == True:
            notification_type = "ABOVE MAX TEMP."

        if notification_type is not None:
            _send_advisor_notifications(deployment, s, notification_type)
            _send_client_notifications(deployment, s, notification_type)
            _store_notification(deployment.id, s.id, channel_id, s.safeguard_temp_lower, s.safeguard_temp_upper, temp)

    except Deployment.DoesNotExist:
        raise HttpResponse(status=404)

def _ok_to_send_notification(last_notification_sent):
    an_hour = timedelta(seconds=60*60)
    if last_notification_sent is not None:
        if datetime.now(last_notification_sent.tzinfo) < (last_notification_sent + an_hour):
            return False
        else:
            return True
    else:
        return True

def _send_advisor_notifications(deployment, sensor, notification_type):
    if _ok_to_send_notification(sensor.last_advisor_notification_sent):
        email_subj = "Project 137: %s for client %s" % (notification_type, deployment.client_name)
        email_msg = "Thermal safeguaring notification recieved.\n\n Warning room %s for Client %s and sensor %s." % (notification_type, deployment.client_name, sensor.location, )
        txt_msg = "Warning %s for Client %s and sensor %s" % (notification_type, deployment.client_name, sensor.location)

        _send_notification_email(email_subj, email_msg, notification_type, deployment.advisor_email)
        _send_notification_sms(txt_msg, deployment.advisor_phone)

        sensor.last_advisor_notification_sent = datetime.today()
        sensor.save()

def _send_client_notifications(deployment, sensor, notification_type):
    dt = datetime.now()
    time_now = dt.time()

    if _ok_to_send_notification(sensor.last_notification_sent) and deployment.should_send_client_notifications(dt.weekday(), time_now):
        email_subj = "Room %s is %s" % (sensor.location, notification_type)
        email_msg =  "Hello %s, your %s is %s your desired temperature. We will be in touch with you soon to discuss this" % (deployment.client_name, sensor.location, notification_type)
        txt_msg = email_msg

        _send_notification_email(email_subj, email_msg, notification_type, deployment.client_email)
        _send_notification_sms(email_msg, deployment.client_phone)

        sensor.last_notification_sent = datetime.today()
        sensor.save()

def _store_notification(deployment_id, sensor_deployment_id, channel_id, lower_limit, upper_limit, value):
    notification = {
        "measurement": "SAFEGUARD",
        "tags": {
            "deployment": deployment_id,
            "sensor_deployment": sensor_deployment_id,
            "channel": channel_id
        },
        "fields": {
            "value" : value,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit
        }
    }
    influx.write_points([notification])

def _send_notification_sms(msg, to):
    if to is not None:
        data =  urllib.parse.urlencode({'apikey': "", 'numbers': to, 'message' : msg, 'sender': "HomeEnergy"})
        data = data.encode('utf-8')
        request = urllib.request.Request("https://api.txtlocal.com/send/?")
        f = urllib.request.urlopen(request, data)
        fr = f.read()
        return(fr)

def _send_notification_email(subj, msg_text, notification_type, to):
    if to is not None:
        from_addr = "Home Energy Team <nhm-support@cse.org.uk>"
        date = datetime.now()
        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( from_addr, to, subj, date, msg_text )

        server = smtplib.SMTP_SSL('', 587)
        server.ehlo()
        server.login("", "")
        server.sendmail("nhm-support@cse.org.uk", to, msg)
        server.quit()
