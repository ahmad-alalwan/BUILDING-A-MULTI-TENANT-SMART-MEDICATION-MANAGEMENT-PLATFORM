from django.http import Http404
from .models import Tenant

class TenantMiddleware:
    """Middleware to identify tenant from request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get tenant from request
        tenant = self.get_tenant_from_request(request)
        request.tenant = tenant
        
        response = self.get_response(request)
        return response
    
    def get_tenant_from_request(self, request):
        """Extract tenant from request headers or domain"""
        # Method 1: From X-Tenant header
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                return Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Method 2: From X-Tenant-Name header
        tenant_name = request.headers.get('X-Tenant-Name')
        if tenant_name:
            try:
                return Tenant.objects.get(name=tenant_name, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Method 3: From domain
        host = request.get_host().split(':')[0]
        try:
            return Tenant.objects.get(domain=host, is_active=True)
        except Tenant.DoesNotExist:
            pass
        
        # Method 4: Default tenant
        try:
            return Tenant.objects.get(name='Default Tenant', is_active=True)
        except Tenant.DoesNotExist:
            # Create default tenant if it doesn't exist
            return Tenant.objects.create(
                name='Default Tenant',
                domain='default.local'
            )
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view to ensure tenant is available"""
        if not hasattr(request, 'tenant'):
            request.tenant = self.get_tenant_from_request(request)
        return None
