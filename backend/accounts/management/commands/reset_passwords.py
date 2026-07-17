from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Force resets default user passwords'

    def handle(self, *args, **kwargs):
        users = [
            ('principal@drngpit.ac.in', 'Admin@123'),
            ('management@drngpit.ac.in', 'Admin@123'),
        ]
        
        for email, password in users:
            try:
                user = User.objects.get(username=email)
                user.set_password(password)
                user.first_login_completed = False  # Force them to change it again
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully reset password for {email} to {password}"))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User {email} not found!"))
