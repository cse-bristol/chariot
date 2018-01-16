import datetime
import json
from django.utils.timezone import now, timedelta

from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse, StreamingHttpResponse
from django.views.generic import DetailView

from chariot import utils
from chariot.influx import select, influx
from chariot.mixins import BackButtonMixin, LoginRequiredMixin
from deployments.models import Deployment, DeploymentAnnotation
from graphs import simplify


def query(deployment, sensor, channel, start=None, end=None, aggregation="30m"):
    query_obj = select("MEAN").from_table(channel.id) \
        .where('deployment').eq(deployment.pk) \
        .where('sensor').eq(sensor.id)
    if start:
        query_obj = query_obj.where('time').gte(start)

    if end:
        query_obj = query_obj.where('time').lte(end)

    if not start and not end:
        query_obj = query_obj.where('time').lte_now()

    query_obj = query_obj.group_by_time(aggregation).fill_none().limit(10000)

    return query_obj.fetch()


def generate_data(deployment_id, sensors=None, channels=None, simplified=True, start=None,
                  end=None):
    try:
        yield '{"sensors":['
        deployment = Deployment.objects.get(pk=deployment_id)
        first_sensor = True
        for sensor in deployment.sensors.all():
            if sensors and sensor.sensor.id not in sensors:
                continue
            if first_sensor:
                first_sensor = False
            else:
                yield ','
            yield '{"id":' + sensor.sensor.id + ','
            yield '"name":"' + sensor.sensor.name + '",'
            yield '"location":"' + sensor.location + '",'
            if sensor.cost:
                yield '"cost":' + str(sensor.cost) + ','
            yield '"channels":['

            first_channel = True
            for channel in sensor.sensor.channels.all():
                if channels != 'all' and (
                            channel.hidden or (channels and channel.id not in channels)):
                    continue
                aggregation = channel.aggregation
                if not simplified:
                    aggregation = '10s'
                response = query(deployment, sensor.sensor, channel, start, end,
                                 aggregation)
                first_value = True
                while response.has_data():
                    if simplified:
                        data = simplify.simplify(response.data, 0.3)
                    else:
                        data = response.data
                    for value in data:
                        if first_value:
                            first_value = False
                            if first_channel:
                                first_channel = False
                            else:
                                yield ','
                            yield '{"id":"' + channel.id + '",'
                            yield '"name":"' + channel.name + '",'
                            yield '"units":"' + channel.units + '",'
                            yield '"data":['
                        else:
                            yield ','
                        yield '{"time":' + str(value['time']) + ','
                        yield '"value":' + str(value['mean']) + '}'

                    if response.is_partial():
                        response.next()
                    else:
                        break

                if not first_value:
                    yield ']}'

            yield ']}'
        yield '],'
        yield '"annotations":['
        annotations = DeploymentAnnotation.objects.filter(deployment=deployment_id)
        first_annotation = True
        for annotation in annotations:
            if first_annotation:
                first_annotation = False
            else:
                yield ','
            obj = utils.to_dict(annotation)
            yield json.dumps(obj)
        yield ']}'
    except Exception as e:
        yield e


def get_all_data(request, pk):
    return StreamingHttpResponse(generate_data(pk), content_type="application/json")


class DeploymentPredictionView(LoginRequiredMixin, BackButtonMixin, DetailView):
    model = Deployment
    template_name = 'graphs/deployment_prediction.html'

    def get_back_url(self):
        return reverse('deployments:update', args=(self.object.id,))


class DeploymentGraphView(LoginRequiredMixin, BackButtonMixin, DetailView):
    model = Deployment
    template_name = 'graphs/deployment_graph.html'

    def get_back_url(self):
        return reverse('deployments:update', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(DeploymentGraphView, self).get_context_data(**kwargs)
        deployment = self.get_object()

        if deployment.start_date is None:
            raise Http404("Deployment not started")

        context['dateTo'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context['dateFrom'] = max(deployment.start_date,  now() - timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S")
        
        return context

class DeploymentAlertView(LoginRequiredMixin, BackButtonMixin, DetailView):
    model = Deployment
    template_name = 'graphs/deployment_alert_history.html'

    def get_back_url(self):
        return reverse('deployments:update', args=(self.object.id,))

    @staticmethod
    def format_alert(alert, sensor_deployments):
        sensor_deployment_id = alert["sensor_deployment"]
        sensor_deployment_id = int(sensor_deployment_id) if sensor_deployment_id is not None else None
        channel_id = alert["channel"]

        ## It would be more convenient to use deployment.sensors.get(pk = sensor_deployment_id)
        ## However, this would result in many more database queries, which is slow
        ## Instead, we preload everything (shouldn't be very much data) and filter it in Python
        sensor_deployment = [sd for sd in sensor_deployments if sd.id == sensor_deployment_id]
        sensor_deployment = sensor_deployment[0] if len(sensor_deployment) == 1 else None
        sensor = sensor_deployment.sensor if sensor_deployment else None

        if sensor:
            channel = [channel for channel in sensor.channels.all() if channel.id == channel_id]
            channel = channel[0] if len(channel) == 1 else None

            measurement = channel.name if channel else None
        else:
            measurement = ""

        return {
            "datetime": alert["time"][0:10] + " " + alert["time"][12:19],
            "value": alert["value"],
            "location": sensor_deployment.location if sensor_deployment else "",
            "measurement": measurement,
            "lower_limit": alert["lower_limit"],
            "upper_limit": alert["upper_limit"]
        }

    def get_context_data(self, **kwargs):
        context = super(DeploymentAlertView, self).get_context_data(**kwargs)
        deployment = self.get_object()

        sensor_deployments = deployment.sensors.all().prefetch_related("sensor__channels")

        context["alerts"] = [
            DeploymentAlertView.format_alert(alert, sensor_deployments) for alert in influx.query(
                "SELECT value, deployment, sensor_deployment, channel, lower_limit, upper_limit FROM SAFEGUARD ORDER BY time DESC LIMIT 10000"
            ).get_points()
        ]

        return context
