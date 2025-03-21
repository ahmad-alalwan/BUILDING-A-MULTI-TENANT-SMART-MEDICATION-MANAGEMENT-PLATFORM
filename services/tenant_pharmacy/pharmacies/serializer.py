from rest_framework import serializers
from .models import *
class Medicine_serializer(serializers.ModelSerializer):
    class Meta:
        model=Medicine
        fields='__all__' 

class Register_serializer(serializers.ModelSerializer):
    class Meta:
        model=Register_Financial
        fields='__all__'    

class Register_pharmacy_serializer(serializers.ModelSerializer):
    class Meta:
        model=Register_pharmacy
        fields=('name_medicine','quantity','date')        
