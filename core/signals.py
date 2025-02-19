from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def assign_admin_role_to_superuser(sender, instance, created, **kwargs):
    """
    Automatically set the role to 'admin' if the user is newly created and is a superuser.
    """
    if created and instance.is_superuser:
        if instance.role != 'admin':
            instance.role = 'admin'
            # Use update_fields to avoid re-triggering the post_save signal unnecessarily
            instance.save(update_fields=['role'])
