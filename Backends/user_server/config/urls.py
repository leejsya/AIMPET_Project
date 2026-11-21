from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/users/admin/', admin.site.urls),
    path('api/users/', include('user_app.urls')),
]
