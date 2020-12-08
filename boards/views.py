from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from boards import models


def _get_recently_seen_devices(limit=5):
    with connection.cursor() as cursor:
        query = "select a.* from "


@login_required()
def homepage(request, *args, **kwargs):
    last_seen_devices = models.Sensor
    return render(request, 'home.html')


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
