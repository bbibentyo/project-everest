from django.contrib import admin
from django.urls import path
from boards import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.homepage),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('api/remote/upload/', views.SensorDataView.as_view())
]
