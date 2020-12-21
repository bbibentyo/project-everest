from rest_framework import serializers

from boards import models


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensor
        fields = ['identifier', 'name', 'color', 'location', 'comments']
