#from deployments.signals import sensor_reading_recieved
#from django.dispatch import reciever
from chariot.influx import influx
from deployments.models import Deployment, DeploymentSensor
from datetime import timedelta, datetime
import smtplib

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

def _send_notifications(deployment,sensor,value):
    if _ok_to_send_notification(sensor.last_notification_sent):
        _send_notification_email(deployment,sensor,"XXX")
        sensor.last_notification_sent = datetime.today()
        sensor.save()

def _ok_to_send_notification(last_notification_sent):
    an_hour = timedelta(seconds=60*60)
    an_hour = timedelta(seconds=20) ##TODO REMOVE BEFORE COMMIT
    if last_notification_sent is not None and datetime.now(last_notification_sent.tzinfo) < (last_notification_sent + an_hour):
        return False
    else:
        return True

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


def _send_notification_email(deployment,sensor,notification_type):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    #server.starttls()
    server.login("membershipmanagerdemo@gmail.com", "PASSWORD")
    
    msg = "\nHello!"
    server.sendmail("you@gmail.com", "richard.tiffin@cse.org.uk", msg)
    server.quit()
    
