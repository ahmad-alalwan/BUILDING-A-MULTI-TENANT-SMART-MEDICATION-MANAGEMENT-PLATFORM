from django.core.management.base import BaseCommand
from auth.token_services import TokenAuthService

class Command(BaseCommand):
    help = 'Clean up expired access tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it',
        )

    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('DRY RUN - No tokens will be actually cleaned up')
        
        # Clean up expired tokens
        cleaned_count = TokenAuthService.cleanup_expired_tokens()
        
        if cleaned_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleaned up {cleaned_count} expired tokens')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No expired tokens found to clean up')
            )
