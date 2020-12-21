from django.contrib import admin
from boards import models


@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'identifier', 'name', 'color', 'owner', 'date_created')


class ProximityInline(admin.TabularInline):
    model = models.ProximityData


@admin.register(models.SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sensor', 'date_received', 'temperature', 'humidity',
                    'x_coordinate', 'y_coordinate', 'z_coordinate')
    list_filter = ('sensor', 'date_received')
    inlines = [ProximityInline]


@admin.register(models.ProximityData)
class ProximityDataAdmin(admin.ModelAdmin):
    list_display = ('batch', 'target', 'distance')
    list_filter = ['target']
