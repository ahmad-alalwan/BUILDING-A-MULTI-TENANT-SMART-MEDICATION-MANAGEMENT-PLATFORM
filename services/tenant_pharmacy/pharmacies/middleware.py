from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant_model

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        hostname = request.get_host().split(':')[0]
        TenantModel = get_tenant_model()
        try:
            tenant = TenantModel.objects.get(domain_url=hostname)
            request.tenant = tenant
        except TenantModel.DoesNotExist:
            request.tenant = None   