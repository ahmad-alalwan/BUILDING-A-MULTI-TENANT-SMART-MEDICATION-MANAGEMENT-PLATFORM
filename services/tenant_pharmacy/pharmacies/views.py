from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view 
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializer import*
from .Producer import *
# Create your views here.
@api_view(['GET'])
def search_mdicine(request,pk):
    item=Medicine.objects.get(name=pk)
    if request.method == 'GET':
        serializer=Medicine_serializer(item) 
        producer = ProducerUserCreated()
        message = { 'value': item.name}
        producer.publish(message)
        return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['PUT'])
def sale(request,pk):
    item=Medicine.objects.get(name=pk)
    if request.method=='PUT':
        quantity_old=item.quantity
        quantity_new=quantity_old-1
        item.quantity = quantity_new
        item.save()
        serializer=Medicine_serializer(item)  
        return Response(serializer.data,status=status.HTTP_201_CREATED)
             
@api_view(['POST'])
def register_add(request, pk1, pk2):
    if request.method == 'POST':
        name_medicine = pk1
        quantity = pk2
        if name_medicine is None or quantity is None:
            return Response({'error': 'Name and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        tenant = request.tenant
        if not tenant:
            return Response({'error': 'Tenant not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'name_medicine': name_medicine, 'quantity': quantity}
        
        serializer = Register_pharmacy_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            tenant_id = tenant.schema_name  
            producer = ProducerUserCreated(tenant_id)
            producer.publish("user.created", data)  
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def reqistes_show(request):
    item=Register_pharmacy.objects.all()    
    if request.method=='GET':
        serializer=Register_pharmacy_serializer(item,many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
      
@api_view(['POST'])
def add_Medicien(request):
    if request.method == 'POST':
        tenant = request.tenant
        if not tenant:
            return Response({'error': 'Tenant not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = Medicine_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # Publish the data to Kafka
            tenant_id = tenant.schema_name  
            producer = ProducerUserCreated(tenant_id)
            try:
                producer.publish("medicine.added", request.data) 
            except Exception as e:
                print(f"Failed to publish message to Kafka: {e}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET']) 
def all_medicine(request):
    item=Medicine.objects.all()
    if request.method == 'GET':
        serializer=Medicine_serializer(item ,many=True) 
        return Response(serializer.data,status=status.HTTP_200_OK)   
           
@api_view(["GET"])
def all_order(request):
    tenant = request.tenant
    if not tenant:
        return Response({'error': 'Tenant not found.'}, status=status.HTTP_400_BAD_REQUEST)
    
    items = Register_pharmacy.objects.filter(tenant=tenant).order_by('date')
    
    if request.method == 'GET':
        serializer = Register_pharmacy_serializer(items, many=True)
        
        tenant_id = tenant.schema_name  
        producer = ProducerUserCreated(tenant_id)
        try:
            producer.publish("order.retrieved", serializer.data)  
        except Exception as e:
            print(f"Failed to publish message to Kafka: {e}")
        
        return Response(serializer.data, status=status.HTTP_200_OK)
