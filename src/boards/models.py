from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Sensor(models.Model):
    identifier = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    comments = models.CharField(max_length=250, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)

    @property
    def readable_name(self):
        return self.name or self.identifier or self.pk

    def __str__(self):
        return self.readable_name

    class Meta:
        verbose_name_plural = 'Sensor'


class SensorData(models.Model):
    date_received = models.DateTimeField(default=timezone.now)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    x_coordinate = models.FloatField(default=0)
    y_coordinate = models.FloatField(default=0)
    z_coordinate = models.FloatField(default=0)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name_plural = 'Sensor Data'


class ProximityData(models.Model):
    batch = models.ForeignKey(SensorData, on_delete=models.CASCADE)
    target = models.ForeignKey(Sensor, related_name='target_device', on_delete=models.CASCADE)
    distance = models.FloatField()

    class Meta:
        unique_together = [('batch', 'target')]
        verbose_name_plural = 'Proximity Data'
