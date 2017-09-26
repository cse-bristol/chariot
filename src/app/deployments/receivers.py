#from deployments.signals import sensor_reading_recieved
#from django.dispatch import reciever
from chariot.influx import influx
from deployments.models import Deployment, DeploymentSensor

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
        elif deployment.safeguards_on == True and temp > max_temp:
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
    
