from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    # admin 페이지
    path('api/inf/admin/', admin.site.urls),
    # app 페이지
    path('api/inf/', include('inf_app.urls')),
    # 미디어 페이지
    re_path(r'^api/inf/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
