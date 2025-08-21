from django.core.management.base import BaseCommand
from auth.models import Tenant, Role

class Command(BaseCommand):
    help = 'Create initial tenants and roles for multi-tenant system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-name',
            type=str,
            help='Name of the tenant to create',
        )
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain for the tenant',
        )

    def handle(self, *args, **options):
        tenants_data = [
            {
                'name': 'Default Tenant',
                'domain': 'default.local'
            },
            {
                'name': 'Company A',
                'domain': 'companya.local'
            },
            {
                'name': 'Company B',
                'domain': 'companyb.local'
            }
        ]

        # Add custom tenant if provided
        if options['tenant_name']:
            tenants_data.append({
                'name': options['tenant_name'],
                'domain': options['domain'] or f"{options['tenant_name'].lower().replace(' ', '')}.local"
            })

        created_tenants = 0
        created_roles = 0

        for tenant_data in tenants_data:
            tenant, tenant_created = Tenant.objects.get_or_create(
                name=tenant_data['name'],
                defaults={
                    'domain': tenant_data['domain'],
                    'is_active': True
                }
            )
            
            if tenant_created:
                created_tenants += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created tenant: {tenant.name} (Domain: {tenant.domain})')
                )
                
                # Create roles for this tenant
                roles_data = [
                    {
                        'name': 'admin',
                        'description': 'Administrator with full system access'
                    },
                    {
                        'name': 'expert',
                        'description': 'Expert user with limited administrative access'
                    },
                    {
                        'name': 'user',
                        'description': 'Regular user with basic access'
                    }
                ]
                
                for role_data in roles_data:
                    role, role_created = Role.objects.get_or_create(
                        tenant=tenant,
                        name=role_data['name'],
                        defaults={'description': role_data['description']}
                    )
                    
                    if role_created:
                        created_roles += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  - Created role: {role.name}')
                        )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tenant already exists: {tenant.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_tenants} new tenants and {created_roles} new roles')
        )
