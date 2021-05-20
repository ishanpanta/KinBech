from django.contrib import admin
from django.urls import path, include

# for static
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "KinBech Administration"
admin.site.site_title = "KinBech Admin Panel"
admin.site.index_title = "Welcome to KinBech Admin Panel"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace="app")),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
