from django.db import models
from datetime import*
from django.db import connection

# Create your models here.
       
class Medicine(models.Model):
    name=models.CharField(max_length=50,unique=True,blank=True)
    quantity=models.IntegerField()
    price=models.CharField(max_length=50)
    def __str__(self):
        return self.name   
        
class Register_Financial(models.Model):
    account=models.IntegerField()
    invoice=models.IntegerField(primary_key=True)
    
class Register_pharmacy(models.Model):
    id=models.BigAutoField(primary_key=True)
    name_medicine=models.CharField(max_length=50)
    quantity=models.IntegerField()
    date=models.DateTimeField(default=datetime.now)
    def __str__(self):
        return str(self.name_medicine)

    

    


    