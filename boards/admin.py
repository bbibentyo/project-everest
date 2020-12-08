from django.contrib import admin
from boards import models


@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'identifier', 'name', 'owner', 'date_created')


@admin.register(models.SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sensor', 'temperature', 'humidity',
                    'x_coordinate', 'y_coordinate', 'z_coordinate')


@admin.register(models.ProximityData)
class ProximityDataAdmin(admin.ModelAdmin):
    list_display = ('batch', 'target', 'distance')
