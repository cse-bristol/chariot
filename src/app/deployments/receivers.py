#from deployments.signals import sensor_reading_recieved
#from django.dispatch import reciever
from chariot.influx import influx
from deployments.models import Deployment

#@reciever(sensor_reading_recieved)
def receive_notification(sender, deployment_pk, sensor, temp):
    #Get thermal bounds for sensor
    try:
        d = Deployment.objects.get(pk=deployment_pk)
        if d.safeguards_on == True:
            _store_notification(deployment_pk,sensor,temp)
    except Deployment.DoesNotExist:
        raise HttpResponse(status=404)

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
    
