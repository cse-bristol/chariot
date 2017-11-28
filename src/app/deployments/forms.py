from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput

from hubs.models import Hub
from sensors.models import Sensor
from .models import Deployment, DeploymentSensor, DeploymentAnnotation, AlertScheduleDay
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *


class NumberInput(TextInput):
    input_type = 'number'


class DeploymentAddHubForm(forms.ModelForm):
    class Meta:
        fields = ['hub']
        model = Deployment
        widgets = {
            'hub': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(DeploymentAddHubForm, self).__init__(*args, **kwargs)

        self.fields['hub'].label = "Hub Identifier"

    def clean_hub(self):
        hub = self.cleaned_data['hub']

        if self.instance.hub:
            raise forms.ValidationError(
                "There is already a hub assigned to this deployment.")

        try:
            old_deployment = hub.deployment
            old_deployment.hub = None
            old_deployment.save()
        except (AttributeError, Deployment.DoesNotExist):
            pass

        return hub


class DeploymentAnnotationForm(forms.ModelForm):
    class Meta:
        fields = ['start', 'end', 'layer', 'deployment', 'text']
        model = DeploymentAnnotation

    start = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'])
    end = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'])


class DeploymentUpdateForm(forms.ModelForm):
    address_line_one = forms.CharField(label='First Line of Address')

    class Meta:
        fields = [
            'photo',
            'client_name',
            'address_line_one',
            'post_code',
            'notes',
            'building_area',
            'building_height',
            'boiler_manufacturer',
            'boiler_type',
            'boiler_thermostat',
            'boiler_model',
            'boiler_output',
            'boiler_efficiency',
            'safeguards_on',
            'advisor_email',
            'advisor_phone',
            'client_email',
            'client_phone'
        ]
        model = Deployment

class DeploymentCreateForm(forms.ModelForm):
    hub = forms.ModelChoiceField(queryset=Hub.objects.filter(deployment__isnull=True),
                                 empty_label=None)

    def save(self, commit=True):
        # TODO Check hub
        instance = super(DeploymentCreateForm, self).save(commit=False)
        if commit:
            instance.save()

        # Create DeploymentSensors for all default sensors
        sensors = Sensor.objects.filter(default=True)
        for sensor in sensors:
            sensor_deployment = DeploymentSensor(sensor=sensor,
                                                 deployment=instance,
                                                 location=sensor.name)
            sensor_deployment.save()

        return instance

    class Meta:
        fields = [
            'hub',
            'photo',
            'client_name',
            'address_line_one',
            'post_code',
            'notes',
            'building_area',
            'building_height',
            'boiler_manufacturer',
            'boiler_type',
            'boiler_thermostat',
            'boiler_model',
            'boiler_output',
            'boiler_efficiency',
            'safeguards_on',
            'advisor_email',
            'advisor_phone',
            'client_email',
            'client_phone']
        model = Deployment


class DeploymentEndForm(forms.ModelForm):
    class Meta:
        fields = ['id']
        model = Deployment

    def save(self, commit=True):
        self.instance.end()


class DeploymentStartForm(forms.ModelForm):
    class Meta:
        fields = ['id']
        model = Deployment

    def save(self, commit=True):
        self.instance.start()


class DeploymentSensorUpdateForm(forms.ModelForm):
    location = forms.CharField()
    cost = forms.FloatField(required=False)

    class Meta:
        fields = ['location', 'cost', 'nearest_thermostat', 'room_area', 'room_height', 'safeguard_temp_lower', 'safeguard_temp_upper','last_notification_sent','last_advisor_notification_sent','notifications_on']
        model = DeploymentSensor


class DeploymentSensorCreateForm(forms.ModelForm):
    class Meta:
        fields = ['deployment', 'sensor', 'location']
        model = DeploymentSensor
        widgets = {
            'deployment': forms.HiddenInput(),
            'sensor': forms.HiddenInput()
        }

class AlertScheduleDayUpdateForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(
        choices = (
            (0, 'Mon'),
            (1, 'Tue'),
            (2, 'Wed'),
            (3, 'Thu'),
            (4, 'Fri'),
            (5, 'Sat'),
            (6, 'Sun')))

    class Meta:
        fields = [
            'day_of_week',
            'client_notifications_from_1', 'client_notifications_to_1',
            'client_notifications_from_2', 'client_notifications_to_2',
            'client_notifications_from_3', 'client_notifications_to_3'
            ]
        model = AlertScheduleDay

    def _clean_client_notifications(self, period):
        from_name = "client_notifications_from_" + str(period)
        to_name = "client_notifications_to_" + str(period)

        from_val = self.cleaned_data.get(from_name)
        to_val = self.cleaned_data.get(to_name)

        if (from_val is None and to_val is None):
            return
        elif (from_val is None and to_val is not None):
            self.add_error(from_name, ValidationError("Start time missing."))
        elif (from_val is not None and to_val is None):
            self.add_error(to_name, ValidationError("End time missing."))
        elif from_val >= to_val:
            self.add_error(from_name, ValidationError("Start time must be before end time."))

    def clean(self):
        for period in [1, 2, 3]:
            self._clean_client_notifications(period)

DeploymentScheduleFormset = forms.inlineformset_factory(Deployment,
                                                        AlertScheduleDay,
                                                        form=AlertScheduleDayUpdateForm,
                                                        extra=7,
                                                        max_num=7,
                                                        can_delete=False,
                                                        can_order=False)
