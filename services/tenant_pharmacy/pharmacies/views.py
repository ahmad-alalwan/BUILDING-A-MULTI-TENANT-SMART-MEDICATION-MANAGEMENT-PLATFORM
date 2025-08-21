from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import *
from .serializer import*

# Medicine Views
class MedicineListCreateView(ListCreateAPIView):
    """
    GET: List all medicines
    POST: Create a new medicine
    """
    queryset = Medicine.objects.all()
    serializer_class = Medicine_serializer

class MedicineDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific medicine by ID
    PUT/PATCH: Update a specific medicine
    DELETE: Delete a specific medicine
    """
    queryset = Medicine.objects.all()
    serializer_class = Medicine_serializer
    lookup_field = 'id'

class MedicineSearchView(APIView):
    """
    GET: Search medicine by name
    """
    def get(self, request, name):
        try:
            item = Medicine.objects.get(name=name)
            serializer = Medicine_serializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)

class MedicineSaleView(APIView):
    """
    PUT: Decrease medicine quantity by 1 (sale operation)
    """
    def put(self, request, name):
        try:
            item = Medicine.objects.get(name=name)
            quantity_old = item.quantity
            quantity_new = quantity_old - 1
            if quantity_new < 0:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = quantity_new
            item.save()
            serializer = Medicine_serializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)

# Register_Financial Views
class RegisterFinancialListCreateView(ListCreateAPIView):
    """
    GET: List all financial registers
    POST: Create a new financial register
    """
    queryset = Register_Financial.objects.all()
    serializer_class = Register_serializer

class RegisterFinancialDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific financial register by invoice
    PUT/PATCH: Update a specific financial register
    DELETE: Delete a specific financial register
    """
    queryset = Register_Financial.objects.all()
    serializer_class = Register_serializer
    lookup_field = 'invoice'

# Register_pharmacy Views
class RegisterPharmacyListCreateView(ListCreateAPIView):
    """
    GET: List all pharmacy registers
    POST: Create a new pharmacy register
    """
    queryset = Register_pharmacy.objects.all()
    serializer_class = Register_pharmacy_serializer

class RegisterPharmacyDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific pharmacy register by ID
    PUT/PATCH: Update a specific pharmacy register
    DELETE: Delete a specific pharmacy register
    """
    queryset = Register_pharmacy.objects.all()
    serializer_class = Register_pharmacy_serializer
    lookup_field = 'id'

class RegisterPharmacyOrderedView(APIView):
    """
    GET: List all pharmacy registers ordered by date
    """
    def get(self, request):
        items = Register_pharmacy.objects.order_by('date')
        serializer = Register_pharmacy_serializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterPharmacyAddView(APIView):
    """
    POST: Add a new pharmacy register with name and quantity parameters
    """
    def post(self, request, name_medicine, quantity):
        if name_medicine is None or quantity is None:
            return Response({'error': 'Name and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'name_medicine': name_medicine, 'quantity': quantity}
        serializer = Register_pharmacy_serializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

