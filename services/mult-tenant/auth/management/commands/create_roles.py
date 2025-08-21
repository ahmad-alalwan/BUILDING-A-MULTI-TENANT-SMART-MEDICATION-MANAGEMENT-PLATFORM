from django.core.management.base import BaseCommand
from auth.models import Role

class Command(BaseCommand):
    help = 'Create initial roles for the system'

    def handle(self, *args, **options):
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

        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new roles')
        )
