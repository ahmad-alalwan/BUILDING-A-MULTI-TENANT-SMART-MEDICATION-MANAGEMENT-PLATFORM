from django.shortcuts import render
from django.urls import reverse
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response

class TenantDataView(APIView):
    def get(self, request ,tenant_name):
        tenant = Client.objects.get(name=tenant_name)
        return Response({"name": tenant.id, "id": tenant.schema_name})      