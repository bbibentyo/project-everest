from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from boards import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.homepage),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('ping/', views.ping),
    path('api/remote/upload/', views.SensorDataView.as_view()),
    path('api/sensors/', views.CreateSensorView.as_view()),
    path('api/temperature/', views.device_temperature, name='device_temperature'),
    path('api/humidity/', views.device_temperature, name='device_humidity')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
