import datetime

import pandas as pd

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from boards import models

date_format = '%Y-%m-%d %H:%M'


def _get_recently_seen_devices(limit=5):
    query = """with devices as (select bs.identifier, max(bs2.date_received) as last_seen
from boards_sensor bs join boards_sensordata bs2 on bs.id = bs2.sensor_id
group by bs.identifier)
select IFNULL(bs.name, d.identifier), d.last_seen from devices d join boards_sensor bs on d.identifier = bs.identifier
order by last_seen desc limit %s"""

    with connection.cursor() as cursor:
        cursor.execute(query, [limit])
        devices = cursor.fetchall()
    return devices


@login_required()
def homepage(request, *args, **kwargs):
    return render(request, 'home.html', context={'devices': _get_recently_seen_devices()})


def _hourly_range(delta=24):
    previous = (timezone.now().replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=delta))
    return [(previous + datetime.timedelta(minutes=30*x)).strftime(date_format) for x in range(delta * 2)]


def device_temperature(request, *args, **kwargs):
    last_24_hours = timezone.now() - datetime.timedelta(days=2)
    objects = models.SensorData.objects.select_related('sensor').filter(
        date_received__gte=last_24_hours).order_by('-date_received')
    frame = pd.DataFrame(
        [dict(device=x.sensor.readable_name,
              x=x.date_received, y=x.temperature, borderColor=x.sensor.color)
         for x in objects])

    labels = _hourly_range(48)
    datasets = []
    frame['x'] = frame['x'].dt.strftime(date_format)
    for name, g in frame.groupby('device'):
        res = {'label': name, 'data': g[['x', 'y']].to_dict(orient='records'),
               'fill': False, 'borderColor': g['borderColor'].any()}
        datasets.append(res)
    results = {'labels': labels, 'datasets': datasets}
    return JsonResponse(results, safe=False)


def device_humidity(request, *args, **kwargs):
    last_24_hours = timezone.now() - datetime.timedelta(days=2)
    objects = models.SensorData.objects.select_related('sensor').filter(
        date_received__gte=last_24_hours).order_by('-date_received')
    frame = pd.DataFrame(
        [dict(device=x.sensor.readable_name,
              x=x.date_received, y=x.humidity, borderColor=x.sensor.color)
         for x in objects])

    labels = _hourly_range(48)
    datasets = []
    frame['x'] = frame['x'].dt.strftime(date_format)
    for name, g in frame.groupby('device'):
        res = {'label': name, 'data': g[['x', 'y']].to_dict(orient='records'),
               'fill': False, 'borderColor': g['borderColor'].any()}
        datasets.append(res)
    results = {'labels': labels, 'datasets': datasets}
    return JsonResponse(results, safe=False)


def login_view(request, *args, **kwargs):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/home')
            else:
                # Return a 'disabled account' error message
                return render(request, 'auth/login.html')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('/login')


class SensorDataView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        parts = list(map(str.strip, data.split(",")))
        if len(parts) < 6:
            return Response({'error': 'invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        sensor, created = models.Sensor.objects.get_or_create(identifier=parts[0])
        sensor_data = models.SensorData(
            sensor=sensor, temperature=float(parts[1]), humidity=float(parts[2]),
            x_coordinate=float(parts[3]), y_coordinate=float(parts[4]),
            z_coordinate=float(parts[5]))
        sensor_data.save()

        if len(parts) > 7:
            for device in parts[7:]:
                if not device:
                    continue
                neighbor, distance = device.split(":")
                neighbor_sensor, created = models.Sensor.objects.get_or_create(identifier=neighbor)
                proximity = models.ProximityData(
                    batch=sensor_data, target=neighbor_sensor, distance=float(distance))
                proximity.save()
        return Response({}, status=status.HTTP_201_CREATED)
