from django.db import models
from django_tenants.models import TenantMixin ,DomainMixin

class TenantManager(models.Manager):
    def create_tenant(self, name):
        tenant = self.create(name=name)
        return tenant

class Client(TenantMixin):
    name=models.CharField(max_length=220)
    craeted_on=models.DateTimeField(auto_now_add=True)

    objects = TenantManager()
    def __str__(self):
        return self.name 



class Domain(DomainMixin):
    pass


     