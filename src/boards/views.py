import datetime

import pandas as pd

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from boards import models, serializer

date_format = '%Y-%m-%d %H:%M'


def _get_recently_seen_devices(limit=5):
    query = """with devices as (select bs.identifier, max(bs2.sensor_date_time) as last_seen
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
        sensor_date_time__gte=last_24_hours).order_by('-sensor_date_time')
    frame = pd.DataFrame(
        [dict(device=x.sensor.readable_name,
              x=x.sensor_date_time, y=x.temperature, borderColor=x.sensor.color)
         for x in objects])

    if frame.empty:
        return JsonResponse({'datasets': []})

    datasets = []
    frame['x'] = frame['x'].dt.strftime(date_format)
    for name, g in frame.groupby('device'):
        res = {'label': name, 'data': g[['x', 'y']].to_dict(orient='records'),
               'fill': False, 'borderColor': g['borderColor'].any()}
        datasets.append(res)
    results = {'datasets': datasets}
    return JsonResponse(results, safe=False)


def device_humidity(request, *args, **kwargs):
    last_24_hours = timezone.now() - datetime.timedelta(days=2)
    objects = models.SensorData.objects.select_related('sensor').filter(
        sensor_date_time__gte=last_24_hours).order_by('-sensor_date_time')
    frame = pd.DataFrame(
        [dict(device=x.sensor.readable_name,
              x=x.sensor_date_time, y=x.humidity,
              borderColor=x.sensor.color)
         for x in objects])

    if frame.empty:
        return JsonResponse({'datasets': []})

    datasets = []
    frame['x'] = frame['x'].dt.strftime(date_format)
    for name, g in frame.groupby('device'):
        res = {'label': name, 'data': g[['x', 'y']].to_dict(orient='records'),
               'fill': False, 'borderColor': g['borderColor'].any()}
        datasets.append(res)
    results = {'datasets': datasets}
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


def _parse_sensor_data_and_add(data):
    parts = list(map(str.strip, data.split(",")))
    if len(parts) < 3:
        return dict(name=data, status=False)

    try:
        sensor, created = models.Sensor.objects.get_or_create(identifier=parts[0])
        if created:
            print(f"adding new sensor: {parts[0]}")

        sensor_data = models.SensorData(
            sensor=sensor, temperature=float(parts[1]), humidity=float(parts[2]))
        sensor_data.save()
    except Exception as e:
        print(f"error occurred when saving node data: {parts[0]}")
        print(f"{e}")
        return dict(name=parts[0], status=False)

    if len(parts) > 3:
        number_of_neighbors = int(parts[3])
        if number_of_neighbors > 0:
            for device in parts[4:]:
                if not device:
                    print("skipping null device")
                    continue
                try:
                    neighbor, distance = device.split(":")
                    print(f"adding proximity for device: {neighbor} -> distance: {distance}")
                    neighbor_sensor, created = models.Sensor.objects.get_or_create(identifier=neighbor)
                    proximity = models.ProximityData(
                        batch=sensor_data, target=neighbor_sensor, distance=float(distance))
                    proximity.save()
                except Exception as e:
                    print("exception occurred when saving proximity data")
                    print(f"{e}")
                    continue
    return dict(name=sensor.name, status=True)


def _create_sensor_value_from_dict(data):
    if 'name' not in data:
        return dict(name=None, status=False)

    try:
        sensor, _ = models.Sensor.objects.get_or_create(identifier=data['name'])
        sensor_data = models.SensorData(
            sensor=sensor, temperature=data['temperature'],
            humidity=data['humidity'],
            sensor_date_time=data.get('date', timezone.now()))
        sensor_data.save()
    except Exception as e:
        print(f"error occurred when saving node data: {data['name']}")
        print(f"{e}")
        return dict(name=data['name'], status=True)

    neighbors = data.get('neighbors', [])
    print(f"sensor has {len(neighbors)} neighbors")

    for neighbor in neighbors:
        try:
            print(f"adding proximity for device: {neighbor['name']} -> distance: {neighbor['distance']}")
            neighbor_sensor, _ = models.Sensor.objects.get_or_create(identifier=neighbor['name'])
            proximity = models.ProximityData(
                batch=sensor_data, target=neighbor_sensor,
                distance=neighbor['distance'])
            proximity.save()
        except Exception as e:
            print("exception occurred when saving proximity data")
            print(f"{e}")
            continue
    return dict(name=sensor.name, status=True)


class SensorDataView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_response_status(self, results):
        return status.HTTP_201_CREATED if any(x['status'] for x in results) else status.HTTP_400_BAD_REQUEST

    def post(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, str):  # when user sends a single string as sensor value
            lines = data.split('\n')
            results = [_parse_sensor_data_and_add(line) for line in lines]
            print(f"processed {len(results)} sensor data values")
            return Response(results, status=self._get_response_status(results))
        elif isinstance(data, dict):
            results = [_create_sensor_value_from_dict(data)]
            print(f"processed {len(results)} sensor data values")
            return Response(results, status=self._get_response_status(results))
        elif isinstance(data, list):  # it must be a list of dictionaries or individual string
            results = []
            for item in data:
                if isinstance(item, str):
                    results.append(_parse_sensor_data_and_add(item))
                else:
                    results.append(_create_sensor_value_from_dict(item))
            return Response(results, status=self._get_response_status(results))
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


class CreateSensorView(ListCreateAPIView):
    queryset = models.Sensor.objects.all()
    serializer_class = serializer.SensorSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]


def ping(request, *args, **kwargs):
    return JsonResponse({'status': 'alive'}, safe=True, status=status.HTTP_200_OK)
