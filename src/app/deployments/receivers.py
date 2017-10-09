#from deployments.signals import sensor_reading_recieved
#from django.dispatch import reciever
from chariot.influx import influx
from deployments.models import Deployment, DeploymentSensor
from datetime import timedelta, datetime, time
import smtplib
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

        min_temp = s.safeguard_temp_lower
        max_temp = s.safeguard_temp_upper
        
        if deployment.safeguards_on == True and temp < min_temp:
             _store_notification(deployment_pk,sensor,temp)
             _send_notifications(deployment,s,temp)
             
        elif deployment.safeguards_on == True and temp > max_temp:
            _send_notifications(deployment,s,temp)
            _store_notification(deployment_pk,s,temp)
             
    except Deployment.DoesNotExist:
        raise HttpResponse(status=404)

def _send_notifications(deployment,sensor,notification_type):
    _send_client_notification(deployment, sensor, notification_type)
    
def _ok_to_send_notification(last_notification_sent):
    an_hour = timedelta(seconds=60*60)
    an_hour = timedelta(seconds=20) ##TODO REMOVE BEFORE COMMIT
    if last_notification_sent is not None and datetime.now(last_notification_sent.tzinfo) < (last_notification_sent + an_hour):
        return False
    else:
        return True

def _send_client_notification(deployment, sensor, notification_type):
    time_now = datetime.now(sensor.last_notification_sent.tzinfo).time()
    email_msg = "Message content %s" % (deployment.client_notifications_from < time_now)

    if _ok_to_send_notification(sensor.last_notification_sent) and deployment.client_notifications_from < time_now and time_now < deployment.client_notifications_to:
        if deployment.client_email is not None:
            _send_notification_email(email_msg, notification_type, deployment.client_email)

        if deployment.client_phone is not None:
            _send_notification_sms(email_msg, deployment.client_phone)

        sensor.last_notification_sent = datetime.today()
        sensor.save()
                                
def _store_notification(deployment,sensor_id,value):
    notification = {
        "measurement": "SAFEGUARD",
        "tags": {
            "deployment": deployment,
            "sensor": sensor_id
        },
        "fields": {
            "value" : value
        }
    }
    influx.write_points([notification])

def _send_notification_sms(msg, to):
    data =  urllib.parse.urlencode({'apikey': "", 'numbers': to,
                                    'message' : msg, 'sender': "CSE"})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.txtlocal.com/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)
    
def _send_notification_email(msg, notification_type, to):
     server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
     server.ehlo()
     server.login("membershipmanagerdemo@gmail.com", "")
     server.sendmail("you@gmail.com", to, msg)
     server.quit()
    
