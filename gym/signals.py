from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import os

@receiver(post_migrate)
def create_initial_admin(sender, **kwargs):
    if sender.name == 'gym':
        User = get_user_model()
        username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin@gmail.com')
        email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@gmail.com')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'Admin123*')
        
        if not User.objects.filter(role='administrator').exists():
            print("Creating initial administrator user...")
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role='administrator'
            )
            print("Administrator user created successfully!")