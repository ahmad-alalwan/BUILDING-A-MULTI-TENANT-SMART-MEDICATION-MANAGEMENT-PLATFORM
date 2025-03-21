from django.urls import path
from django.contrib import admin
from .admin import tenant_admin_site
from .views import TenantDataView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('manager/',tenant_admin_site.urls),
    path('api/<str:tenant_name>/', TenantDataView.as_view()),

]
