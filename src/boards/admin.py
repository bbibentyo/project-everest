from django.contrib import admin
from boards import models


@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'identifier', 'name', 'color', 'owner', 'date_created')


class ProximityInline(admin.TabularInline):
    model = models.ProximityData


@admin.register(models.SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sensor', 'sensor_date_time', 'date_created', 'temperature', 'humidity')
    list_filter = ('sensor', 'sensor_date_time', 'date_created')
    inlines = [ProximityInline]


@admin.register(models.ProximityData)
class ProximityDataAdmin(admin.ModelAdmin):
    list_display = ('batch', 'target', 'distance')
    list_filter = ['target']
